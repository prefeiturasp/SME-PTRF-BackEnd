import json
from decimal import Decimal

import pytest

pytestmark = pytest.mark.django_db


def test_tabela_valores_pendentes(
    jwt_authenticated_client_a,
    acao_associacao_role_cultural,
    acao_associacao_ptrf,
    conta_associacao_cartao,
    periodo_2020_1,
    receita_2019_2_role_repasse_conferida,
    receita_2019_2_role_repasse_conferida_no_periodo,
    receita_2020_1_role_repasse_conferida,
    receita_2020_1_ptrf_repasse_conferida,
    receita_2020_1_role_repasse_cheque_conferida,
    receita_2020_1_role_outras_conferida,
    receita_2020_1_role_repasse_nao_conferida,
    receita_2020_1_role_outras_nao_conferida,
    despesa_2019_2,
    rateio_despesa_2019_role_conferido,
    rateio_despesa_2019_role_conferido_no_periodo,
    despesa_2020_1,
    rateio_despesa_2020_role_conferido,
    rateio_despesa_2020_role_nao_conferido,
    rateio_despesa_2020_ptrf_conferido,
    rateio_despesa_2020_role_cheque_conferido,
    fechamento_periodo_2019_2_1000,
    fechamento_periodo_2019_2_role_1000

):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/tabela-valores-pendentes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_associacao_cartao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'saldo_anterior': Decimal('2000.00'),
        'receitas_conciliadas': Decimal('400.00'),
        'despesas_conciliadas': Decimal('300.00'),
        'despesas_nao_conciliadas': Decimal('100.00'),
        'receitas_nao_conciliadas': Decimal('200.00'),
        'despesas_total': Decimal('400.00'),
        'receitas_total': Decimal('600.00'),
        'saldo_posterior_conciliado': Decimal('2100.00'),
        'saldo_posterior_nao_conciliado': Decimal('2100.00'),
        'saldo_posterior_total': Decimal('2200.00'),
    }

    assert result == esperado
