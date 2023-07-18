import pytest
from sme_ptrf_apps.core.services import lancamentos_da_prestacao

pytestmark = pytest.mark.django_db


def test_get_lancamentos_da_analise_da_prestacao_conferencia_correto(
    jwt_authenticated_client_a,
    rateio_despesa_2020_inativa_conferencia_correto,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_teste_conferencia,
    analise_prestacao_conta_2020_1_em_analise_conferencia_correto,
    analise_lancamento_despesa_prestacao_conta_2020_1_conferencia_correto,
    despesa_2020_1_inativa_conferencia_correto,
    tipo_transacao,
):
    filtro_conferencia_list = ['CORRETO']  # Deve trazer 01 lancamento

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_conferencia_correto,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtro_conferencia_list=filtro_conferencia_list
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_inativa_conferencia_correto.uuid}'


def test_get_lancamentos_da_analise_da_prestacao_conferencia_ajuste(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_teste_conferencia,
    rateio_despesa_2020_inativa_conferencia_ajuste,
    analise_prestacao_conta_2020_1_em_analise_conferencia_ajuste,
    analise_lancamento_despesa_prestacao_conta_2020_1_conferencia_ajuste,
    despesa_2020_1_inativa_conferencia_ajuste,
    tipo_transacao,
):
    filtro_conferencia_list = ['AJUSTE']  # Deve trazer 01 lancamento

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_conferencia_ajuste,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtro_conferencia_list=filtro_conferencia_list
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_inativa_conferencia_ajuste.uuid}'


def test_get_lancamentos_da_analise_da_prestacao_conferencia_conferencia_automatica(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_teste_conferencia,
    rateio_despesa_2020_inativa_conferencia_automatica,
    analise_prestacao_conta_2020_1_em_analise_conferencia_automatica,
    analise_lancamento_despesa_prestacao_conta_2020_1_conferencia_automatica,
    despesa_2020_1_inativa_conferencia_automatica,
    receita_conferencia_automatica,
    tipo_transacao,
):
    filtro_conferencia_list = ['CONFERENCIA_AUTOMATICA']  # Deve trazer 02 lancamento. Uma despesa e uma receita

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_conferencia_automatica,
        conta_associacao=conta_associacao_cartao,
        filtro_conferencia_list=filtro_conferencia_list
    )

    assert len(lancamentos) == 2


def test_get_lancamentos_da_analise_da_prestacao_conferencia_nao_conferido(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_teste_conferencia,
    rateio_despesa_2020_inativa_nao_conferido,
    analise_prestacao_conta_2020_1_em_analise_nao_conferido,
    despesa_2020_1_inativa_nao_conferido,
    receita_nao_conferido,
    tipo_transacao,
):
    filtro_conferencia_list = ['NAO_CONFERIDO']  # Deve trazer 02 lancamento. Uma despesa e uma receita

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_nao_conferido,
        conta_associacao=conta_associacao_cartao,
        filtro_conferencia_list=filtro_conferencia_list
    )

    assert len(lancamentos) == 2


def test_get_lancamentos_da_analise_da_prestacao_conferencia_todos(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_teste_conferencia,

    rateio_despesa_2020_inativa_conferencia_correto,
    despesa_2020_1_inativa_conferencia_correto,

    rateio_despesa_2020_inativa_conferencia_ajuste,
    despesa_2020_1_inativa_conferencia_ajuste,

    rateio_despesa_2020_inativa_conferencia_automatica,
    despesa_2020_1_inativa_conferencia_automatica,
    receita_conferencia_automatica,

    rateio_despesa_2020_inativa_nao_conferido,
    despesa_2020_1_inativa_nao_conferido,
    receita_nao_conferido,
    tipo_transacao,

    analise_prestacao_conta_2020_1_em_analise_todos,
    analise_lancamento_despesa_prestacao_conta_todos_01,
    analise_lancamento_despesa_prestacao_conta_2020_1_todos_02,
    analise_lancamento_despesa_prestacao_conta_2020_1_todos_03,

):
    filtro_conferencia_list = ['NAO_CONFERIDO', 'CONFERENCIA_AUTOMATICA', 'AJUSTE',
                               'CORRETO']  # Deve trazer 06 lancamento.

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise_todos,
        conta_associacao=conta_associacao_cartao,
        filtro_conferencia_list=filtro_conferencia_list
    )

    assert len(lancamentos) == 6
