import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_create_analise_valor_reprogramado(jwt_authenticated_client_a, analise_prestacao_conta_2020_1,
                                                  conta_associacao,
                                                  acao_associacao):
    payload_nova_analise = {
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": f'{conta_associacao.uuid}',
        "acao_associacao": f'{acao_associacao.uuid}',
        "valor_saldo_reprogramado_correto": True,
        "novo_saldo_reprogramado_custeio": None,
        "novo_saldo_reprogramado_capital": None,
        "novo_saldo_reprogramado_livre": None
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-valores-reprogramados/salvar-valores-reprogramados-acao/',
        data=json.dumps(payload_nova_analise), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        "mensagem": "Analise de valores reprogramados salva com sucesso"
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_action_create_analise_valor_reprogramado_falha_payload_nao_enviado(jwt_authenticated_client_a,
                                                                      analise_prestacao_conta_2020_1,
                                                                      conta_associacao,
                                                                      acao_associacao):
    payload_nova_analise = None

    response = jwt_authenticated_client_a.post(
        f'/api/analises-valores-reprogramados/salvar-valores-reprogramados-acao/',
        data=json.dumps(payload_nova_analise), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'Dados da Análise Vazio',
        'mensagem': 'Os dados da análise não foram enviados'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_action_create_analise_valor_reprogramado_falha_falta_analise(jwt_authenticated_client_a,
                                                                      analise_prestacao_conta_2020_1,
                                                                      conta_associacao,
                                                                      acao_associacao):
    payload_nova_analise = {
        "conta_associacao": f'{conta_associacao.uuid}',
        "acao_associacao": f'{acao_associacao.uuid}',
        "valor_saldo_reprogramado_correto": True,
        "novo_saldo_reprogramado_custeio": None,
        "novo_saldo_reprogramado_capital": None,
        "novo_saldo_reprogramado_livre": None
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-valores-reprogramados/salvar-valores-reprogramados-acao/',
        data=json.dumps(payload_nova_analise), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'Dados incompletos',
        'mensagem': 'Não foram enviados todos os dados necessários'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_action_create_analise_valor_reprogramado_falha_uuid_conta_errado(jwt_authenticated_client_a,
                                                                      analise_prestacao_conta_2020_1,
                                                                      conta_associacao,
                                                                      acao_associacao):
    conta_associacao_uuid = 'uuid_errado'

    payload_nova_analise = {
        "analise_prestacao_conta": f'{analise_prestacao_conta_2020_1.uuid}',
        "conta_associacao": f'{conta_associacao_uuid}',
        "acao_associacao": f'{acao_associacao.uuid}',
        "valor_saldo_reprogramado_correto": True,
        "novo_saldo_reprogramado_custeio": None,
        "novo_saldo_reprogramado_capital": None,
        "novo_saldo_reprogramado_livre": None
    }

    response = jwt_authenticated_client_a.post(
        f'/api/analises-valores-reprogramados/salvar-valores-reprogramados-acao/',
        data=json.dumps(payload_nova_analise), content_type='application/json')

    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'Objeto não encontrado.',
        'mensagem': f"O objeto conta-associação para o uuid {conta_associacao_uuid} não foi encontrado na base."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado

