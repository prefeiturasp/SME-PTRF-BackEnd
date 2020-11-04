import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_info_devolucoes_ao_tesouro_relatorio(jwt_authenticated_client, dre, periodo, tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {'tipo': 'Devolução ao tesouro tipo 1', 'ocorrencias': 999, 'valor': 3000.00},
        {'tipo': 'Devolução ao tesouro tipo 2', 'ocorrencias': 100, 'valor': 2000.00},
        {'tipo': 'Devolução ao tesouro tipo 3', 'ocorrencias': 200, 'valor': 1000.00},
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passa_dre(jwt_authenticated_client, dre, periodo, tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?periodo={periodo.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid da dre. ?dre=uuid_da_dre',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passa_periodo(jwt_authenticated_client, dre, periodo,
                                                                      tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&tipo_conta={tipo_conta.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado


def test_api_get_info_devolucoes_ao_tesouro_relatorio_sem_passar_tipo_conta(jwt_authenticated_client, dre, periodo,
                                                                          tipo_conta):
    response = jwt_authenticated_client.get(
        f'/api/relatorios-consolidados-dre/info-devolucoes-ao-tesouro/?dre={dre.uuid}&periodo={periodo.uuid}',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'erro': 'falta_de_informacoes',
        'mensagem': 'Faltou informar o uuid do tipo de conta. ?tipo_conta=uuid_do_tipo_conta',
        'operacao': 'info-devolucoes-ao-tesouro'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == resultado_esperado
