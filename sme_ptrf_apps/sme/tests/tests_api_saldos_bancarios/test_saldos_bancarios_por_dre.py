import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_saldo_bancario_por_dre(jwt_authenticated_client_sme, observacao_conciliacao_saldos_bancarios,
                                periodo_saldos_bancarios,
                                tipo_conta_saldos_bancarios,
                                dre,
                                dre_saldos_bancarios,
                                ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2

def test_saldo_bancario_por_dre_com_conta_nao_iniciada(jwt_authenticated_client_sme,
                                observacao_conciliacao_saldos_bancarios,
                                observacao_conciliacao_saldos_bancarios_com_conta_nao_iniciada,
                                periodo_saldos_bancarios,
                                tipo_conta_saldos_bancarios,
                                dre,
                                dre_saldos_bancarios,
                                ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_saldo_bancario_por_dre_com_conta_encerrada(jwt_authenticated_client_sme,
                                observacao_conciliacao_saldos_bancarios,
                                observacao_conciliacao_saldos_bancarios_com_conta_encerrada,
                                solicitacao_encerramento_conta_aprovada,
                                periodo_saldos_bancarios,
                                tipo_conta_saldos_bancarios,
                                dre,
                                dre_saldos_bancarios,
                                ):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}&conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_saldo_bancario_por_dre_falta_periodo(jwt_authenticated_client_sme, tipo_conta_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?conta={tipo_conta_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-dre',
        'mensagem': 'Faltou informar o uuid do periodo. ?periodo=uuid_do_periodo'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_saldo_bancario_por_dre_falta_conta(jwt_authenticated_client_sme, periodo_saldos_bancarios):
    response = jwt_authenticated_client_sme.get(
        f'/api/saldos-bancarios-sme/saldo-por-dre/?periodo={periodo_saldos_bancarios.uuid}',
        content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'operacao': 'saldo-por-dre',
        'mensagem': 'Faltou informar o uuid da conta. ?conta=uuid_da_conta'
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
