import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_get_analise_valor_reprogramado(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-valores-reprogramados/valores-reprogramados-acao/?analise_prestacao_conta={analise_prestacao_conta_2020_1.uuid}&conta_associacao={conta_associacao.uuid}&acao_associacao={acao_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = [{
        "uuid": f'{analise_valor_reprogramado_por_acao.uuid}',
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": f'{conta_associacao.uuid}',
        "acao_associacao": f'{acao_associacao.uuid}',
        "valor_saldo_reprogramado_correto": False,
        "novo_saldo_reprogramado_custeio": "1.00",
        "novo_saldo_reprogramado_capital": "2.00",
        "novo_saldo_reprogramado_livre": "3.00"
    }]

    assert response.status_code == status.HTTP_200_OK
    assert esperado == result


def test_action_get_analise_valor_reprogramado_falha_sem_analise_pc(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-valores-reprogramados/valores-reprogramados-acao/?conta_associacao={conta_associacao.uuid}&acao_associacao={acao_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid da análise da PC.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert esperado == result


def test_action_get_analise_valor_reprogramado_falha_sem_conta_associacao(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-valores-reprogramados/valores-reprogramados-acao/?analise_prestacao_conta={analise_prestacao_conta_2020_1.uuid}&acao_associacao={acao_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid da conta da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert esperado == result


def test_action_get_analise_valor_reprogramado_falha_sem_acao_associacao(
    jwt_authenticated_client_a,
    analise_valor_reprogramado_por_acao,
    analise_prestacao_conta_2020_1,
    conta_associacao,
    acao_associacao
):
    response = jwt_authenticated_client_a.get(
        f'/api/analises-valores-reprogramados/valores-reprogramados-acao/?analise_prestacao_conta={analise_prestacao_conta_2020_1.uuid}&conta_associacao={conta_associacao.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário enviar o uuid da ação da associação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert esperado == result

