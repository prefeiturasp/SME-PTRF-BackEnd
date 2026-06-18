import pytest
from unittest.mock import patch

from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.services.valida_geracao_documentos_service import (
    ValidaGeracaoDocumentoPAAService,
    ValidaGeracaoDocumentoException,
)

pytestmark = pytest.mark.django_db

PREVIA = DocumentoPaa.VersaoChoices.PREVIA
FINAL = DocumentoPaa.VersaoChoices.FINAL
EM_PROCESSAMENTO = DocumentoPaa.StatusChoices.EM_PROCESSAMENTO
CONCLUIDO = DocumentoPaa.StatusChoices.CONCLUIDO


def _paa_em_elaboracao(paa_factory):
    paa = paa_factory()
    assert paa.status_em_elaboracao
    return paa


def _paa_em_retificacao(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_em_retificacao()
    return paa


def _paa_gerado(paa_factory):
    paa = paa_factory()
    paa.set_paa_status_gerado()
    return paa


# valida_gerar_documento_previa
class TestValidaGerarDocumentoPrevia:

    def test_paa_em_elaboracao_sem_documentos_passa(self, paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_paa_em_retificacao_bloqueia(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="PAA está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_paa_gerado_bloqueia(self, paa_factory):
        paa = _paa_gerado(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="O PAA não está em elaboração"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_paa_status_none_bloqueia(self, paa_factory):
        paa = paa_factory()
        paa.status = None
        paa.save()
        with pytest.raises(ValidaGeracaoDocumentoException, match="O PAA não está em elaboração"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_previa_em_processamento_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        with pytest.raises(ValidaGeracaoDocumentoException, match="prévia em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_final_em_processamento_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        with pytest.raises(ValidaGeracaoDocumentoException, match="final em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_final_concluido_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=CONCLUIDO, retificacao=False)
        with pytest.raises(ValidaGeracaoDocumentoException, match="Já existe uma versão final gerada"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_previa_concluida_nao_bloqueia(self, paa_factory, documento_paa_factory):
        """Uma prévia concluída não deve bloquear a geração de nova prévia."""
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=CONCLUIDO, retificacao=False)
        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_documento_retificacao_em_processamento_nao_bloqueia_original(self, paa_factory, documento_paa_factory):
        """
        Documentos de retificação (retificacao=True) não devem bloquear a geração
        do documento original — os filtros são isolados por retificacao=False.
        """
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=EM_PROCESSAMENTO, retificacao=True)
        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)

    def test_prioridade_de_verificacao_retificacao_antes_de_elaboracao(self, paa_factory):
        """
        Se o PAA está EM_RETIFICACAO, a primeira exceção deve ser sobre retificação,
        não sobre elaboração — a ordem das checagens importa.
        """
        paa = _paa_em_retificacao(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="PAA está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa(paa)


# valida_gerar_documento_final
class TestValidaGerarDocumentoFinal:
    """
    valida_gerar_documento_final delega para valida_gerar_documento_previa;
    testamos que a delegação funciona e que os cenários de bloqueio se aplicam.
    """

    def test_paa_em_elaboracao_sem_documentos_passa(self, paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa)

    def test_paa_em_retificacao_bloqueia(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="PAA está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa)

    def test_previa_em_processamento_bloqueia_geracao_final(self, paa_factory, documento_paa_factory):
        """
        Há uma geração de prévia em processamento deve bloquear a geração do final
        (a mensagem orienta o usuário a aguardar).
        """
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        with pytest.raises(ValidaGeracaoDocumentoException, match="prévia em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa)

    def test_final_concluido_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=CONCLUIDO, retificacao=False)
        with pytest.raises(ValidaGeracaoDocumentoException, match="Já existe uma versão final gerada"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final(paa)


# valida_gerar_documento_previa_retificacao
class TestValidaGerarDocumentoPreviaRetificacao:

    def _mock_alteracoes(self, tem_alteracoes: bool):
        retorno = {"texto_introducao": ["antes", "depois"]} if tem_alteracoes else {}
        return patch(
            "sme_ptrf_apps.paa.services.valida_geracao_documentos_service"
            ".RetificacaoPaaService.identificar_alteracoes",
            return_value=retorno,
        )

    def test_paa_em_elaboracao_bloqueia(self, paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="O PAA não está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_paa_gerado_bloqueia(self, paa_factory):
        paa = _paa_gerado(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="O PAA não está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_previa_retificacao_em_processamento_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=True)
        with pytest.raises(ValidaGeracaoDocumentoException, match="prévia de retificação em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_final_retificacao_em_processamento_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=EM_PROCESSAMENTO, retificacao=True)
        with pytest.raises(ValidaGeracaoDocumentoException, match="retificação final em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_final_retificacao_concluido_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=CONCLUIDO, retificacao=True)
        with pytest.raises(ValidaGeracaoDocumentoException, match="retificação final gerado"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_sem_alteracoes_bloqueia(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with self._mock_alteracoes(tem_alteracoes=False):
            with pytest.raises(ValidaGeracaoDocumentoException, match="Nenhuma alteração encontrada"):
                ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_com_alteracoes_passa(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with self._mock_alteracoes(tem_alteracoes=True):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_previa_retificacao_concluida_nao_bloqueia(self, paa_factory, documento_paa_factory):
        """Uma prévia de retificação concluída não deve bloquear nova geração de prévia."""
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=CONCLUIDO, retificacao=True)
        with self._mock_alteracoes(tem_alteracoes=True):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa)

    def test_usuario_none_e_aceito(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with self._mock_alteracoes(tem_alteracoes=True):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_previa_retificacao(paa, usuario=None)


# valida_gerar_documento_final_retificacao
class TestValidaGerarDocumentoFinalRetificacao:
    """
    valida_gerar_documento_final_retificacao delega para
    valida_gerar_documento_previa_retificacao; testamos a delegação e os casos
    principais para garantir que a cobertura não depende apenas de testes internos.
    """

    def _mock_alteracoes(self, tem_alteracoes: bool):
        retorno = {"texto_introducao": ["antes", "depois"]} if tem_alteracoes else {}
        return patch(
            "sme_ptrf_apps.paa.services.valida_geracao_documentos_service"
            ".RetificacaoPaaService.identificar_alteracoes",
            return_value=retorno,
        )

    def test_paa_em_elaboracao_bloqueia(self, paa_factory):
        paa = _paa_em_elaboracao(paa_factory)
        with pytest.raises(ValidaGeracaoDocumentoException, match="O PAA não está em retificação"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final_retificacao(paa)

    def test_final_retificacao_concluido_bloqueia(self, paa_factory, documento_paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=CONCLUIDO, retificacao=True)
        with pytest.raises(ValidaGeracaoDocumentoException, match="retificação final gerado"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final_retificacao(paa)

    def test_sem_alteracoes_bloqueia(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with self._mock_alteracoes(tem_alteracoes=False):
            with pytest.raises(ValidaGeracaoDocumentoException, match="Nenhuma alteração encontrada"):
                ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final_retificacao(paa)

    def test_com_alteracoes_passa(self, paa_factory):
        paa = _paa_em_retificacao(paa_factory)
        with self._mock_alteracoes(tem_alteracoes=True):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final_retificacao(paa)

    def test_previa_retificacao_em_processamento_bloqueia_final_retificacao(
            self, paa_factory, documento_paa_factory):
        """
        valida_gerar_documento_final_retificacao delega para
        valida_gerar_documento_previa_retificacao, que bloqueia se existe uma prévia
        de retificação EM_PROCESSAMENTO — mesmo que o usuário queira gerar o final.
        """
        paa = _paa_em_retificacao(paa_factory)
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=True)
        with pytest.raises(ValidaGeracaoDocumentoException, match="prévia de retificação em processamento"):
            ValidaGeracaoDocumentoPAAService.valida_gerar_documento_final_retificacao(paa)


# _existe_doc (método privado testado indiretamente via isolamento)
class TestExisteDoc:
    """Testa o método _existe_doc diretamente para garantir o isolamento por campo."""

    def test_retorna_false_sem_documentos(self, paa_factory):
        paa = paa_factory()
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is False

    def test_retorna_true_quando_documento_existe(self, paa_factory, documento_paa_factory):
        paa = paa_factory()
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is True

    def test_isolamento_por_retificacao(self, paa_factory, documento_paa_factory):
        """retificacao=True não deve ser encontrado ao buscar retificacao=False."""
        paa = paa_factory()
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=True)
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is False

    def test_isolamento_por_versao(self, paa_factory, documento_paa_factory):
        """Documento FINAL não é encontrado ao buscar PREVIA."""
        paa = paa_factory()
        documento_paa_factory(paa=paa, versao=FINAL, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is False

    def test_isolamento_por_status(self, paa_factory, documento_paa_factory):
        """Documento CONCLUIDO não é encontrado ao buscar EM_PROCESSAMENTO."""
        paa = paa_factory()
        documento_paa_factory(paa=paa, versao=PREVIA, status_geracao=CONCLUIDO, retificacao=False)
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is False

    def test_isolamento_por_paa(self, paa_factory, documento_paa_factory):
        """Documento de outro PAA não é encontrado."""
        paa_a = paa_factory()
        paa_b = paa_factory()
        documento_paa_factory(paa=paa_b, versao=PREVIA, status_geracao=EM_PROCESSAMENTO, retificacao=False)
        result = ValidaGeracaoDocumentoPAAService._existe_doc(
            paa_a, retificacao=False, versao=PREVIA, status=EM_PROCESSAMENTO
        )
        assert result is False
