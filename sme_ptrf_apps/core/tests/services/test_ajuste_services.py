import pytest

from sme_ptrf_apps.core.services.ajuste_services import possui_apenas_categorias_que_nao_requerem_ata
from sme_ptrf_apps.core.models import (
    AnalisePrestacaoConta, 
    TipoAcertoDocumento, 
    TipoAcertoLancamento
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def prestacao_conta(prestacao_conta_factory):
    return prestacao_conta_factory()


@pytest.fixture
def analise_prestacao_conta(prestacao_conta, analise_prestacao_conta_factory):
    return analise_prestacao_conta_factory(
        prestacao_conta=prestacao_conta,
        status=AnalisePrestacaoConta.STATUS_DEVOLVIDA
    )


@pytest.fixture
def tipo_acerto_documento_ajustes_externos(tipo_acerto_documento_factory):
    return tipo_acerto_documento_factory(
        categoria=TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS
    )


@pytest.fixture
def tipo_acerto_lancamento_ajustes_externos(tipo_acerto_lancamento_factory):
    return tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS
    )


@pytest.fixture
def tipo_acerto_documento_edicao(tipo_acerto_documento_factory):
    return tipo_acerto_documento_factory(
        categoria=TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO
    )


@pytest.fixture
def tipo_acerto_lancamento_edicao(tipo_acerto_lancamento_factory):
    return tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
    )


class TestPossuiApenasCategoriasQueNaoRequeremAta:

    def test_prestacao_conta_none(self):
        assert possui_apenas_categorias_que_nao_requerem_ata(None) is False

    def test_prestacao_conta_sem_analises(self, prestacao_conta):
        assert possui_apenas_categorias_que_nao_requerem_ata(prestacao_conta) is False

    def test_analise_sem_ajustes(self, analise_prestacao_conta):
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_ajustes_externos_documentos(self, analise_prestacao_conta, tipo_acerto_documento_ajustes_externos, analise_documento_prestacao_conta_factory, solicitacao_acerto_documento_factory):
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_ajustes_externos_lancamentos(self, analise_prestacao_conta, tipo_acerto_lancamento_ajustes_externos, analise_lancamento_prestacao_conta_factory, solicitacao_acerto_lancamento_factory):
        
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_solicitacao_de_esclarecimento_documentos(self, analise_prestacao_conta, analise_documento_prestacao_conta_factory, tipo_acerto_documento_factory, solicitacao_acerto_documento_factory):

        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )

        tipo_acerto_esclarecimento = tipo_acerto_documento_factory(
            categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        )

        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_esclarecimento
        )

        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_outros_ajustes_documentos_realizados(self, analise_prestacao_conta, 
                                                           tipo_acerto_documento_ajustes_externos,
                                                           tipo_acerto_documento_edicao,
                                                           analise_documento_prestacao_conta_factory, solicitacao_acerto_documento_factory):
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        # Acerto de edição REALIZADO - deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_outros_ajustes_documentos_nao_realizados(self, analise_prestacao_conta, 
                                                           tipo_acerto_documento_ajustes_externos,
                                                           tipo_acerto_documento_edicao,
                                                           analise_documento_prestacao_conta_factory, solicitacao_acerto_documento_factory):
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        # Acerto de edição NÃO REALIZADO - não deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='PENDENTE'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_outros_ajustes_lancamentos_realizados(self, analise_prestacao_conta,
                                                           tipo_acerto_lancamento_ajustes_externos,
                                                           tipo_acerto_lancamento_edicao,
                                                           analise_lancamento_prestacao_conta_factory, solicitacao_acerto_lancamento_factory):
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        # Acerto de edição REALIZADO - deve gerar ata
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_outros_ajustes_lancamentos_nao_realizados(self, analise_prestacao_conta,
                                                           tipo_acerto_lancamento_ajustes_externos,
                                                           tipo_acerto_lancamento_edicao,
                                                           analise_lancamento_prestacao_conta_factory, solicitacao_acerto_lancamento_factory):
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        # Acerto de edição NÃO REALIZADO - não deve gerar ata
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao,
            status_realizacao='JUSTIFICADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_outros_ajustes_documentos_realizados(self, analise_prestacao_conta, tipo_acerto_documento_edicao, analise_documento_prestacao_conta_factory, solicitacao_acerto_documento_factory):
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto de edição REALIZADO - deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_outros_ajustes_documentos_nao_realizados(self, analise_prestacao_conta, tipo_acerto_documento_edicao, analise_documento_prestacao_conta_factory, solicitacao_acerto_documento_factory):
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto de edição NÃO REALIZADO - não deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='PENDENTE'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_apenas_outros_ajustes_lancamentos_realizados(self, analise_prestacao_conta, tipo_acerto_lancamento_edicao, analise_lancamento_prestacao_conta_factory, solicitacao_acerto_lancamento_factory):
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto de edição REALIZADO - deve gerar ata
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_outros_ajustes_lancamentos_nao_realizados(self, analise_prestacao_conta, tipo_acerto_lancamento_edicao, analise_lancamento_prestacao_conta_factory, solicitacao_acerto_lancamento_factory):
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto de edição NÃO REALIZADO - não deve gerar ata
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao,
            status_realizacao='JUSTIFICADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_documentos_e_lancamentos(self, analise_prestacao_conta,
                                                      tipo_acerto_documento_ajustes_externos,
                                                        tipo_acerto_lancamento_ajustes_externos,
                                                      analise_documento_prestacao_conta_factory,
                                                      analise_lancamento_prestacao_conta_factory,
                                                      solicitacao_acerto_documento_factory,
                                                      solicitacao_acerto_lancamento_factory):
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_ajustes_externos
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_solicitacao_esclarecimento(self, analise_prestacao_conta,
                                                           tipo_acerto_documento_ajustes_externos,
                                                           analise_documento_prestacao_conta_factory,
                                                           analise_lancamento_prestacao_conta_factory,
                                                           solicitacao_acerto_documento_factory,
                                                           solicitacao_acerto_lancamento_factory,
                                                           tipo_acerto_documento_factory):
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        tipo_acerto_esclarecimento = tipo_acerto_documento_factory(
            categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
        )
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_ajustes_externos
        )
        
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_esclarecimento
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_inclusao_credito_realizada(self, analise_prestacao_conta,
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
        
        # Inclusão de crédito REALIZADA - deve gerar ata
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_inclusao_credito,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_inclusao_credito_nao_realizada(self, analise_prestacao_conta,
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
        
        # Inclusão de crédito NÃO REALIZADA - não deve gerar ata
        SolicitacaoAcertoDocumentoFactory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_inclusao_credito,
            status_realizacao='PENDENTE'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_ajustes_externos_com_devolucao_realizada(self, analise_prestacao_conta,
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
        
        # Devolução REALIZADA - deve gerar ata
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_devolucao,
            status_realizacao='REALIZADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_ajustes_externos_com_devolucao_nao_realizada(self, analise_prestacao_conta,
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
        
        # Devolução NÃO REALIZADA - não deve gerar ata
        SolicitacaoAcertoLancamentoFactory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_devolucao,
            status_realizacao='JUSTIFICADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_analise_sem_ajustes_retorna_true(self, analise_prestacao_conta):
        """
        Testa que uma análise sem nenhum acerto retorna True (não requer ata)
        """
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True

    def test_multiplos_acertos_misturados_realizados_e_nao_realizados(self, analise_prestacao_conta,
                                                                    tipo_acerto_documento_edicao,
                                                                    tipo_acerto_lancamento_edicao,
                                                                    analise_documento_prestacao_conta_factory,
                                                                    analise_lancamento_prestacao_conta_factory,
                                                                    solicitacao_acerto_documento_factory,
                                                                    solicitacao_acerto_lancamento_factory):
        """
        Testa cenário com múltiplos acertos: alguns realizados e outros não realizados
        """
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_lancamento = analise_lancamento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto de documento REALIZADO - deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='REALIZADO'
        )
        
        # Acerto de lançamento NÃO REALIZADO - não deve gerar ata
        solicitacao_acerto_lancamento_factory(
            analise_lancamento=analise_lancamento,
            tipo_acerto=tipo_acerto_lancamento_edicao,
            status_realizacao='PENDENTE'
        )
        
        # Como tem pelo menos um acerto realizado que gera ata, deve retornar False
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is False

    def test_apenas_acertos_justificados_retorna_true(self, analise_prestacao_conta,
                                                     tipo_acerto_documento_edicao,
                                                     analise_documento_prestacao_conta_factory,
                                                     solicitacao_acerto_documento_factory):
        """
        Testa que apenas acertos justificados (não realizados) retornam True
        """
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        analise_documento = analise_documento_prestacao_conta_factory(
            analise_prestacao_conta=analise_prestacao_conta
        )
        
        # Acerto apenas JUSTIFICADO - não deve gerar ata
        solicitacao_acerto_documento_factory(
            analise_documento=analise_documento,
            tipo_acerto=tipo_acerto_documento_edicao,
            status_realizacao='JUSTIFICADO'
        )
        
        assert possui_apenas_categorias_que_nao_requerem_ata(analise_prestacao_conta.prestacao_conta) is True
