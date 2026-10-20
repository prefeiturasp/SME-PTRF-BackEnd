import json
from decimal import Decimal
from uuid import uuid4

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_tabela_valores_pendentes_sem_conta_associacao(jwt_authenticated_client_a, periodo_2020_1):
    response = jwt_authenticated_client_a.get(f'/api/conciliacoes/tabela-valores-pendentes/?periodo={periodo_2020_1.uuid}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_tabela_valores_pendentes_sem_periodo(jwt_authenticated_client_a, conta_associacao_cartao):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/tabela-valores-pendentes/?conta_associacao={conta_associacao_cartao.uuid}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'parametros_requeridos'


def test_tabela_valores_pendentes_conta_associacao_nao_encontrada(jwt_authenticated_client_a, periodo_2020_1):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/tabela-valores-pendentes/?periodo={periodo_2020_1.uuid}&conta_associacao={uuid4()}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


def test_tabela_valores_pendentes_periodo_nao_encontrado(jwt_authenticated_client_a, conta_associacao_cartao):
    response = jwt_authenticated_client_a.get(
        f'/api/conciliacoes/tabela-valores-pendentes/?periodo={uuid4()}&conta_associacao={conta_associacao_cartao.uuid}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.content)['erro'] == 'Objeto não encontrado.'


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
        'despesas_conciliadas': 200.0,
        'despesas_nao_conciliadas': 100.0,
        'despesas_outros_periodos': 100.0,
        'despesas_outros_periodos_conciliadas': 100.0,
        'despesas_outros_periodos_nao_conciliadas': 0,
        'despesas_total': 300.0,
        'receitas_conciliadas': 500.0,
        'receitas_nao_conciliadas': 200.0,
        'receitas_total': 700.0,
        'saldo_anterior': 2000.0,
        'saldo_anterior_conciliado': 2000.0,
        'saldo_anterior_nao_conciliado': 0.0,
        'saldo_posterior_conciliado': 2300.0,
        'saldo_posterior_nao_conciliado': 100.0,
        'saldo_posterior_total': 2400.0
    }

    assert result == esperado
