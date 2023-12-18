import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_verifica_saldo_antes_post_saldo_ok(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo,
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/',
                                               data=json.dumps(payload_despesa_valida),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo(
    jwt_authenticated_client_d,
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_outra_acao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
        'saldos_insuficientes': [
            {
                'acao': acao_associacao.acao.nome,
                'aplicacao': 'CUSTEIO',
                'conta': 'Cheque',
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_com_saldo_considerando_livre_aplicacao(
    jwt_authenticated_client_d,
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo_na_conta_com_parametro_nao_aceita_negativo(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_nao_aceita_saldo_negativo_em_conta
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_conta_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
        'saldos_insuficientes': [
            {
                'conta': conta_associacao.tipo_conta.nome,
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': False
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_sem_saldo_na_conta_com_parametro_aceita_negativo(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_aceita_saldo_negativo_em_conta
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_conta_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
        'saldos_insuficientes': [
            {
                'conta': conta_associacao.tipo_conta.nome,
                'saldo_disponivel': 0,
                'total_rateios': 1000.00
            }
        ],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_post_com_saldo_na_conta_considerando_recursos_livre_aplicacao(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida,
    parametros_nao_aceita_saldo_negativo_em_conta,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/', data=json.dumps(payload_despesa_valida),
                           content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_suficiente',
        'mensagem': 'Há saldo disponível para cobertura da despesa.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_despesa_anterior_periodo_inicial(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_valida_anterior_periodo_inicial,
    parametros_nao_aceita_saldo_negativo_em_conta,
    periodo_2020_1,
    fechamento_periodo_com_saldo_livre_aplicacao,
):
    response = jwt_authenticated_client_d.post('/api/rateios-despesas/verificar-saldos/',
                                               data=json.dumps(payload_despesa_valida_anterior_periodo_inicial),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'lancamento_anterior_implantacao',
        'mensagem': 'Lançamento com data anterior ao período inicial da associação.',
        'saldos_insuficientes': [],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)

    assert result == result_esperado
