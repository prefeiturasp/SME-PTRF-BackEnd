import pytest

from sme_ptrf_apps.core.services.ajuste_services import tem_apenas_ajustes_externos
from sme_ptrf_apps.core.models import (
    PrestacaoConta, 
    AnalisePrestacaoConta, 
    TipoAcertoDocumento, 
    TipoAcertoLancamento
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta():
    from sme_ptrf_apps.core.fixtures.factories.prestacao_conta_factory import PrestacaoContaFactory
    return PrestacaoContaFactory()


@pytest.fixture
def analise_prestacao_conta(prestacao_conta):
    from sme_ptrf_apps.core.fixtures.factories.analise_prestacao_conta_factory import AnalisePrestacaoContaFactory
    return AnalisePrestacaoContaFactory(
        prestacao_conta=prestacao_conta,
        status=AnalisePrestacaoConta.STATUS_DEVOLVIDA
    )


@pytest.fixture
def tipo_acerto_documento_ajustes_externos():
    from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_documento_factory import TipoAcertoDocumentoFactory
    return TipoAcertoDocumentoFactory(
        categoria=TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS
    )


@pytest.fixture
def tipo_acerto_lancamento_ajustes_externos():
    from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_lancamento_factory import TipoAcertoLancamentoFactory
    return TipoAcertoLancamentoFactory(
        categoria=TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS
    )


@pytest.fixture
def tipo_acerto_documento_edicao():
    from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_documento_factory import TipoAcertoDocumentoFactory
    return TipoAcertoDocumentoFactory(
        categoria=TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
    )


@pytest.fixture
def tipo_acerto_lancamento_edicao():
    from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_lancamento_factory import TipoAcertoLancamentoFactory
    return TipoAcertoLancamentoFactory(
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
    )


class TestTemApenasAjustesExternos:

    def test_prestacao_conta_none(self):
        assert tem_apenas_ajustes_externos(None) is False

    def test_prestacao_conta_sem_analises(self, prestacao_conta):
        assert tem_apenas_ajustes_externos(prestacao_conta) is False

    def test_analise_sem_ajustes(self, analise_prestacao_conta):
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_ajustes_externos_documentos(self, analise_prestacao_conta, tipo_acerto_documento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_ajustes_externos_lancamentos(self, analise_prestacao_conta, tipo_acerto_lancamento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_lancamento_factory import SolicitacaoAcertoLancamentoFactory
        
        analise_lancamento = AnaliseLancamentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_outros_ajustes_documentos(self, analise_prestacao_conta, 
                                                           tipo_acerto_documento_ajustes_externos,
                                                           tipo_acerto_documento_edicao):
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_outros_ajustes_lancamentos(self, analise_prestacao_conta,
                                                           tipo_acerto_lancamento_ajustes_externos,
                                                           tipo_acerto_lancamento_edicao):
        from sme_ptrf_apps.core.fixtures.factories.analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_lancamento_factory import SolicitacaoAcertoLancamentoFactory
        
        analise_lancamento = AnaliseLancamentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_outros_ajustes_documentos(self, analise_prestacao_conta, tipo_acerto_documento_edicao):
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_outros_ajustes_lancamentos(self, analise_prestacao_conta, tipo_acerto_lancamento_edicao):
        from sme_ptrf_apps.core.fixtures.factories.analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_lancamento_factory import SolicitacaoAcertoLancamentoFactory
        
        analise_lancamento = AnaliseLancamentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_documentos_e_lancamentos(self, analise_prestacao_conta,
                                                      tipo_acerto_documento_ajustes_externos,
                                                      tipo_acerto_lancamento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_lancamento_factory import SolicitacaoAcertoLancamentoFactory
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_lancamento = AnaliseLancamentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_solicitacao_esclarecimento(self, analise_prestacao_conta,
                                                           tipo_acerto_documento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_documento_factory import TipoAcertoDocumentoFactory
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        
        tipo_acerto_esclarecimento = TipoAcertoDocumentoFactory(
            categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        )
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_esclarecimento
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_inclusao_credito(self, analise_prestacao_conta,
                                                  tipo_acerto_documento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_documento_factory import TipoAcertoDocumentoFactory
        from sme_ptrf_apps.core.fixtures.factories.analise_documento_prestacao_conta_factory import AnaliseDocumentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_documento_factory import SolicitacaoAcertoDocumentoFactory
        
        tipo_acerto_inclusao_credito = TipoAcertoDocumentoFactory(
            categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO
        )
        
        analise_documento = AnaliseDocumentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_inclusao_credito
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_devolucao(self, analise_prestacao_conta,
                                           tipo_acerto_lancamento_ajustes_externos):
        from sme_ptrf_apps.core.fixtures.factories.tipo_acerto_lancamento_factory import TipoAcertoLancamentoFactory
        from sme_ptrf_apps.core.fixtures.factories.analise_lancamento_prestacao_conta_factory import AnaliseLancamentoPrestacaoContaFactory
        from sme_ptrf_apps.core.fixtures.factories.solicitacao_acerto_lancamento_factory import SolicitacaoAcertoLancamentoFactory
        
        tipo_acerto_devolucao = TipoAcertoLancamentoFactory(
            categoria=TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
        )
        
        analise_lancamento = AnaliseLancamentoPrestacaoContaFactory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_devolucao
        )
        
        assert tem_apenas_ajustes_externos(analise_prestacao_conta.prestacao_conta) is False
