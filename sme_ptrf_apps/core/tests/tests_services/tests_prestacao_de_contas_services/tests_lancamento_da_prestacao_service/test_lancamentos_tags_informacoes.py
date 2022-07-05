import pytest
from datetime import date

from sme_ptrf_apps.core.services import lancamentos_da_prestacao

pytestmark = pytest.mark.django_db


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

    despesa_2020_1_fornecedor_antonio_jose.data_transacao = date(2020, 3, 9)
    despesa_2020_1_fornecedor_antonio_jose.save()

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


def test_get_lancamentos_da_analise_da_prestacao_com_tag_de_informacao_estornado(
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
    tipo_transacao_pix,
    receita_estorno_do_rateio_despesa_2020_antonio_jose
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
        'tag_id': '2',
        'tag_nome': 'Estornado',
        'tag_hint': 'Esse gasto possui estornos.'
    }, ]
