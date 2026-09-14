import logging

from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa


class DocumentoPaaService:
    def __init__(
        self,
        paa: Paa,
        usuario: str,
        previa: bool,
        logger: logging.Logger,
        retificacao: bool = False,
    ) -> None:
        """Inicializa o serviço com o PAA e o tipo de documento a gerar.

        Args:
            paa: PAA cujo documento será gerado.
            usuario: Identificação do usuário responsável pela geração.
            previa: Indica se o documento é uma prévia.
            logger: Logger usado para registrar o andamento da operação.
            retificacao: Indica se o documento pertence a uma retificação.
        """
        self.paa = paa
        self.usuario = usuario
        self.previa = previa
        self.versao = DocumentoPaa.VersaoChoices.PREVIA if previa else DocumentoPaa.VersaoChoices.FINAL
        self.logger = logger
        self.documento_paa = None
        self.retificacao = retificacao
        self._proxima_versao_documento = None  # calculado antes do delete

        self.logger.info('Inicializando DocumentoPaaService...')

    def apagar_documento_anteriores(self) -> None:
        """Remove documentos anteriores conforme a versão e a retificação atuais."""
        if self.previa:
            """ Em Prévia, remove apenas arquivos de prévia"""
            documentos_anteriores = self.paa.documentopaa_set.filter(
                retificacao=self.retificacao,
                versao=DocumentoPaa.VersaoChoices.PREVIA,
            )
        else:
            """ Em versões finais, remove todos. Se retificação/elaboração, remove todos os respectivos """
            documentos_anteriores = self.paa.documentopaa_set.filter(
                retificacao=self.retificacao,
            )
        self.logger.info(f'Documentos anteriores encontrados {len(documentos_anteriores)}.')

        documentos_anteriores.delete()
        self.logger.info('Documentos anteriores apagados com sucesso.')

    def criar_novo_documento(self) -> None:
        """Obtém ou cria o registro do documento com a versão correspondente."""
        if self.retificacao and self.versao == DocumentoPaa.VersaoChoices.FINAL:
            versao_documento = (self._proxima_versao_documento or 2)
        else:
            versao_documento = 1
        documento, _ = DocumentoPaa.objects.get_or_create(
            paa=self.paa,
            versao=self.versao,
            retificacao=self.retificacao,
            versao_documento=versao_documento,
        )
        self.logger.info(f'Documento PAA versão {self.versao} criado com sucesso.')
        self.documento_paa = documento

    def _calcular_proxima_versao_retificacao(self) -> int:
        """Calcula o próximo número de versão para uma retificação final."""
        ultima = (
            self.paa.documentopaa_set
            .filter(
                retificacao=True,
                versao=DocumentoPaa.VersaoChoices.FINAL)
            .order_by('-versao_documento')
            .values_list('versao_documento', flat=True)
            .first()
        )
        return (ultima or 0) + 1

    def iniciar(self) -> None:
        """Prepara o documento, cria seu registro e marca-o em processamento."""
        if self.retificacao:
            self._proxima_versao_documento = self._calcular_proxima_versao_retificacao()
        self.apagar_documento_anteriores()
        self.criar_novo_documento()
        self.marcar_em_processamento()

    def preparar_documento_para_task(self) -> None:
        """
        Na prévia e na retificação final, o registro EM_PROCESSAMENTO é criado na API antes do Celery.
        """
        if self.previa or self.retificacao:
            doc = self.paa.documentopaa_set.filter(
                versao=self.versao,
                retificacao=self.retificacao,
                status_geracao=DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
            ).first()
            if doc:
                self.documento_paa = doc
                self.logger.info('Documento PAA em processamento reutilizado pela task.')
                return

        self.iniciar()

    def marcar_em_processamento(self) -> None:
        """Marca o documento atual como em processamento."""
        self.documento_paa.arquivo_em_processamento()
        self.logger.info('Documento PAA em processamento')

    def _iniciar_modelo_ata(self) -> None:
        """Inicia o modelo de ata quando a geração final não é uma retificação."""
        if self.previa or self.retificacao:
            return
        from sme_ptrf_apps.paa.models import AtaPaa, Paa

        if isinstance(self.paa, Paa):
            AtaPaa.iniciar(self.paa)

    def marcar_concluido(self) -> None:
        """Marca o documento como concluído e registra as ações relacionadas."""
        self.documento_paa.arquivo_concluido()
        self.registrar_historico_acoes()
        self._iniciar_modelo_ata()
        self.logger.info('Documento PAA concluído')

    def marcar_erro(self) -> None:
        """Marca o documento atual como tendo erro no processamento."""
        self.documento_paa.arquivo_em_erro_processamento()
        self.logger.info('Documento PAA marcado com erro no processamento')

    def registrar_historico_acoes(self) -> None:
        """Registra no histórico as ações do PAA após uma geração final."""
        from sme_ptrf_apps.paa.services import PaaService
        if self.versao == DocumentoPaa.VersaoChoices.FINAL:
            # Registrar as Ações somente na geração final, considerando que, em elaboracao, ainda pode have remoção
            PaaService.registra_historico_acoes(self.paa)
