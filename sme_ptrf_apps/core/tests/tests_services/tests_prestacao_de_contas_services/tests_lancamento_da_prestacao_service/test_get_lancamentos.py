import pytest
from sme_ptrf_apps.core.services import lancamentos_da_prestacao

pytestmark = pytest.mark.django_db


def test_get_todos_lancamentos_da_analise_da_prestacao(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
    )

    assert len(lancamentos) == 3, "Deveria retornar 3 lançamentos 1 despesas e 2 receitas."


def test_get_um_lancamento_receita_da_analise_da_prestacao(
    jwt_authenticated_client_a,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    receita_2020_1_ptrf_repasse_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
    )

    assert len(lancamentos) == 1, "Deveria retornar 1 lançamento de receita."
    assert lancamentos[0]['documento_mestre']['uuid'] == f'{receita_2020_1_ptrf_repasse_conferida.uuid}'


def test_get_lancamentos_da_analise_da_prestacao_filtro_por_fornecedor(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    despesa_2020_1_fornecedor_antonio_jose,
    rateio_despesa_2020_antonio_jose,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
):

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        filtrar_por_nome_fornecedor='jose'
    )

    assert len(lancamentos) == 1
    assert lancamentos[0]['documento_mestre']['uuid'] == f'{despesa_2020_1_fornecedor_antonio_jose.uuid}'


def test_get_lancamentos_da_analise_da_prestacao_filtro_por_forma_pagamento(
    jwt_authenticated_client_a,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    rateio_despesa_2020_role_nao_conferido,
    despesa_2020_1_fornecedor_antonio_jose,
    rateio_despesa_2020_antonio_jose,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_outras_nao_conferida,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix
):

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        tipo_de_pagamento=tipo_transacao_pix,
    )

    assert len(lancamentos) == 1
    assert lancamentos[0]['documento_mestre']['uuid'] == f'{despesa_2020_1_fornecedor_antonio_jose.uuid}'


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_antecipado(
    jwt_authenticated_client_a,
    despesa_2020_1_fornecedor_antonio_jose,
    rateio_despesa_2020_antonio_jose,
    periodo_2020_1,
    conta_associacao_cartao,
    acao_associacao_ptrf,
    prestacao_conta_2020_1_em_analise,
    analise_prestacao_conta_2020_1_em_analise,
    analise_lancamento_receita_prestacao_conta_2020_1_em_analise,
    analise_lancamento_despesa_prestacao_conta_2020_1_em_analise,
    tipo_transacao_pix
):

    lancamentos = lancamentos_da_prestacao(
        analise_prestacao_conta=analise_prestacao_conta_2020_1_em_analise,
        conta_associacao=conta_associacao_cartao,
        tipo_transacao='GASTOS',
        tipo_de_pagamento=tipo_transacao_pix,
    )

    assert len(lancamentos) == 1

    lancamento = lancamentos[0]
    assert lancamento['documento_mestre']['uuid'] == f'{despesa_2020_1_fornecedor_antonio_jose.uuid}'
    assert lancamento['informacoes'] == [{
        'tag_id': '1',
        'tag_nome': 'Antecipado',
        'tag_hint': 'Data do pagamento (09/03/2020) anterior à data do documento (10/03/2020).'
    }, ]
