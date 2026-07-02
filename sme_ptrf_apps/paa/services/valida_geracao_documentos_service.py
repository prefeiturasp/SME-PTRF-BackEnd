from typing import Any, Optional

from sme_ptrf_apps.paa.models import Paa, DocumentoPaa
from sme_ptrf_apps.paa.services.retificacao_paa_service import RetificacaoPaaService
from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService

PREVIA = DocumentoPaa.VersaoChoices.PREVIA
FINAL = DocumentoPaa.VersaoChoices.FINAL
EM_PROCESSAMENTO = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
CONCLUIDO = DocumentoPaa.StatusChoices.CONCLUIDO


class ValidaGeracaoDocumentoException(Exception):
    """ Exceção de Validação de geração de documento PAA."""


class ValidaGeracaoDocumentoPAAService:
    @classmethod
    def _tem_doc_retificacao_novo_neste_ciclo(cls, paa: Paa) -> bool:
        """Verifica se foi gerado novo documento de retificação no ciclo de retificação atual.

        Compara o documento retificado mais recente com o UUID capturado no
        snapshot da réplica ao iniciar a retificação. Retorna True apenas quando
        existe um documento gerado *neste* ciclo, ou seja, com UUID diferente do
        que estava registrado no snapshot.

        Args:
            paa: Instância do PAA em retificação.

        Returns:
            True se um novo documento foi gerado no ciclo atual; False caso contrário.
        """
        return CicloRetificacaoService(paa).tem_documento_final_concluido

    @classmethod
    def _existe_doc(cls,
                    paa: Paa,
                    retificacao: bool,
                    versao: DocumentoPaa.VersaoChoices,
                    status: DocumentoPaa.StatusChoices) -> bool:
        """Verifica se existe documento do PAA com a versão e status informados."""
        return paa.documentopaa_set.filter(
            retificacao=retificacao, versao=versao, status_geracao=status
        ).exists()

    @classmethod
    def valida_gerar_documento_previa(cls, paa: Paa) -> None:
        """
        Validação de geração de documento PAA original prévia.

        Parâmetros:
        - `paa`: Instancia do PAA
        """
        if paa.status_em_retificacao:
            raise ValidaGeracaoDocumentoException("Erro ao gerar documento: PAA está em retificação.")

        if not paa.status_em_elaboracao:
            raise ValidaGeracaoDocumentoException("O PAA não está em elaboração.")

        if cls._existe_doc(paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO):
            raise ValidaGeracaoDocumentoException((
                "Há uma geração de prévia em processamento. "
                "Aguarde a conclusão para gerar a versão final."
            ))

        if cls._existe_doc(paa, retificacao=False, versao=FINAL, status=EM_PROCESSAMENTO):
            raise ValidaGeracaoDocumentoException(
                "Já existe uma geração de documento PAA final em processamento.")

        if cls._existe_doc(paa, retificacao=False, versao=FINAL, status=CONCLUIDO):
            raise ValidaGeracaoDocumentoException(
                "Não é possível gerar o documento. Já existe uma versão final gerada.")

    @classmethod
    def valida_gerar_documento_final(cls, paa: Paa) -> None:
        """
        Validação de geração de documento PAA original final.

        Parâmetros:
        - `paa`: Instancia do PAA
        """
        # atualmente utilizando os mesmos critérios de validação de Prévia Original
        cls.valida_gerar_documento_previa(paa)

    @classmethod
    def valida_gerar_documento_previa_retificacao(cls, paa: Paa, usuario: Optional[Any] = None) -> None:
        """Valida se é possível gerar a prévia do documento de retificação do PAA.

        Args:
            paa: Instância do PAA em retificação.
            usuario: Instância do usuário, vinculado aos loggers de RetificacaoPaaService.

        Raises:
            ValidaGeracaoDocumentoException: Quando o PAA não está em retificação,
                há geração em andamento, já existe documento final gerado no ciclo
                atual, ou não há alterações detectadas em relação ao snapshot.
        """
        if not paa.status_em_retificacao:
            raise ValidaGeracaoDocumentoException("O PAA não está em retificação.")

        if cls._existe_doc(paa, retificacao=True, versao=PREVIA, status=EM_PROCESSAMENTO):
            raise ValidaGeracaoDocumentoException((
                "Há uma geração de prévia de retificação em processamento. "
                "Aguarde a conclusão para gerar a versão final."
            ))

        if cls._existe_doc(paa, retificacao=True, versao=FINAL, status=EM_PROCESSAMENTO):
            raise ValidaGeracaoDocumentoException(
                "Já existe uma geração de documento PAA de retificação final em processamento.")

        if cls._tem_doc_retificacao_novo_neste_ciclo(paa):
            raise ValidaGeracaoDocumentoException(
                "Já existe uma geração de documento PAA de retificação final gerado para esta retificação.")

        alteracoes = RetificacaoPaaService(paa=paa, usuario=usuario).identificar_alteracoes()
        if not alteracoes:
            raise ValidaGeracaoDocumentoException(
                "Nenhuma alteração encontrada. Faça alterações antes de gerar a prévia de retificação.")

    @classmethod
    def valida_gerar_documento_final_retificacao(cls, paa: Paa, usuario: Optional[Any] = None) -> None:
        """Valida se é possível gerar o documento final de retificação do PAA.

        Aplica os mesmos critérios de valida_gerar_documento_previa_retificacao.

        Args:
            paa: Instância do PAA em retificação.
            usuario: Instância do usuário, vinculado aos loggers de RetificacaoPaaService.

        Raises:
            ValidaGeracaoDocumentoException: Quando qualquer critério de prévia falha.
        """
        cls.valida_gerar_documento_previa_retificacao(paa, usuario)
