from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa


class DocumentoPaaService:
    def __init__(self, paa, usuario, previa, logger, retificacao=False):
        self.paa = paa
        self.usuario = usuario
        self.previa = previa
        self.versao = DocumentoPaa.VersaoChoices.PREVIA if previa else DocumentoPaa.VersaoChoices.FINAL
        self.logger = logger
        self.documento_paa = None
        self.retificacao = retificacao
        self._proxima_versao_documento = None  # calculado antes do delete

        self.logger.info('Inicializando DocumentoPaaService...')

    def apagar_documento_anteriores(self):
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

    def criar_novo_documento(self):
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

    def _calcular_proxima_versao_retificacao(self):
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

    def iniciar(self):
        if self.retificacao:
            self._proxima_versao_documento = self._calcular_proxima_versao_retificacao()
        self.apagar_documento_anteriores()
        self.criar_novo_documento()
        self.marcar_em_processamento()

    def preparar_documento_para_task(self):
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

    def marcar_em_processamento(self):
        self.documento_paa.arquivo_em_processamento()
        self.logger.info('Documento PAA em processamento')

    def _iniciar_modelo_ata(self):
        if self.previa or self.retificacao:
            return
        from sme_ptrf_apps.paa.models import AtaPaa, Paa

        if isinstance(self.paa, Paa):
            AtaPaa.iniciar(self.paa)

    def marcar_concluido(self):
        self.documento_paa.arquivo_concluido()
        self.registrar_historico_acoes()
        self._iniciar_modelo_ata()
        self.logger.info('Documento PAA concluído')

    def marcar_erro(self):
        self.documento_paa.arquivo_em_erro_processamento()
        self.logger.info('Documento PAA marcado com erro no processamento')

    def registrar_historico_acoes(self):
        from sme_ptrf_apps.paa.services import PaaService
        if self.versao == DocumentoPaa.VersaoChoices.FINAL:
            # Registrar as Ações somente na geração final, considerando que, em elaboracao, ainda pode have remoção
            PaaService.registra_historico_acoes(self.paa)
