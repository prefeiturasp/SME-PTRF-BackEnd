import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_verifica_saldo_antes_put_saldo_ok(
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
    despesa,
    rateio_despesa_capital,
    payload_despesa_valida
):
    response = jwt_authenticated_client_d.post(f'/api/rateios-despesas/verificar-saldos/?despesa_uuid={despesa.uuid}',
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


def test_api_verifica_saldo_antes_put_sem_saldo(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo,
    fechamento_periodo_com_saldo_outra_acao,
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
    despesa,
    rateio_despesa_capital,
    payload_despesa_valida
):
    # Altera o valor da despesa para um valor além do limite de saldos
    payload_despesa_valida['rateios'][0]['valor_rateio'] = 90000.00

    response = jwt_authenticated_client_d.post(f'/api/rateios-despesas/verificar-saldos/?despesa_uuid={despesa.uuid}',
                          data=json.dumps(payload_despesa_valida),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'situacao_do_saldo': 'saldo_insuficiente',
        'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
        'saldos_insuficientes': [
            {
                'acao': acao_associacao.acao.nome,
                'aplicacao': 'CUSTEIO',
                'saldo_disponivel': 20100.00,
                'total_rateios': 90000.00
            }
        ],
        'aceitar_lancamento': True
    }
    result = json.loads(response.content)
    assert result == result_esperado


def test_api_verifica_saldo_antes_put_saldo_ok_com_saldo_exato_em_fechamento(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_justo,
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
    despesa_justa,
    rateio_despesa_justa,
    payload_despesa_justa
):
    response = jwt_authenticated_client_d.post(f'/api/rateios-despesas/verificar-saldos/?despesa_uuid={despesa_justa.uuid}',
                          data=json.dumps(payload_despesa_justa),
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


def test_api_verifica_saldo_antes_put_saldo_insuficiente_conta_com_saldo_exato_em_fechamento_e_despesa_alterada_para_mais(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_justo,
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
    despesa_justa,
    rateio_despesa_justa,
    payload_despesa_maior
):
    response = jwt_authenticated_client_d.post(f'/api/rateios-despesas/verificar-saldos/?despesa_uuid={despesa_justa.uuid}',
                          data=json.dumps(payload_despesa_maior),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'aceitar_lancamento': True,
        'mensagem': 'Não há saldo disponível em alguma das contas da despesa.',
        'saldos_insuficientes': [
            {
                'conta': 'Cheque',
                'saldo_disponivel': 100.0,
                'total_rateios': 102.0
            }
        ],
        'situacao_do_saldo': 'saldo_conta_insuficiente'
    }
    result = json.loads(response.content)

    assert result == result_esperado


def test_api_verifica_saldo_antes_put_saldo_insuficiente_acao_com_saldo_exato_em_fechamento_e_despesa_alterada_para_mais(
    periodo,
    periodo_2020_1,
    fechamento_periodo_com_saldo_justo,
    fechamento_periodo_com_saldo_justo_outra_acao,
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
    despesa_justa,
    rateio_despesa_justa,
    payload_despesa_maior
):
    response = jwt_authenticated_client_d.post(f'/api/rateios-despesas/verificar-saldos/?despesa_uuid={despesa_justa.uuid}',
                          data=json.dumps(payload_despesa_maior),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result_esperado = {
        'aceitar_lancamento': True,
        'mensagem': 'Não há saldo disponível em alguma das ações da despesa.',
        'saldos_insuficientes': [
            {
                'acao': 'PTRF',
                'aplicacao': 'CUSTEIO',
                'saldo_disponivel': 100.0,
                'total_rateios': 102.0
            }
        ],
        'situacao_do_saldo': 'saldo_insuficiente'
    }
    result = json.loads(response.content)

    assert result == result_esperado
