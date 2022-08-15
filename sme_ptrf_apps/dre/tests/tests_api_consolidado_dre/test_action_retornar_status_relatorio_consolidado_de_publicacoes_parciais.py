import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_get_relatorio_consolidado_de_publicacoes_parciais(dre_teste_api_consolidado_dre, periodo_teste_api_consolidado_dre):
    payload = {
        'dre_uuid': f'{dre_teste_api_consolidado_dre.uuid}',
        'periodo_uuid': f'{periodo_teste_api_consolidado_dre.uuid}',
    }
    return payload


def test_retornar_relatorio_consolidado_de_publicacoes_parciais(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/retorna-status-relatorio-consolidado-de-publicacoes-parciais/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK


def test_retornar_relatorio_consolidado_de_publicacoes_parciais_sem_dre_uuid(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
):
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/trilha-de-status/?periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_retornar_relatorio_consolidado_de_publicacoes_parciais_sem_periodo_uuid(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/trilha-de-status/?dre={dre_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_retornar_relatorio_consolidado_de_publicacoes_parciais_dre_nao_encontrado(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
):
    dre_uuid = f'{dre_teste_api_consolidado_dre.uuid}XX'
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/trilha-de-status/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        "erro": "Objeto não encontrado.",
        "mensagem": f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def retornar_relatorio_consolidado_de_publicacoes_parciais_periodo_nao_encontrado(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid
    periodo_uuid = f"{periodo_teste_api_consolidado_dre.uuid}XX"

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/trilha-de-status/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)
    esperado = {
        "erro": "Objeto não encontrado.",
        "mensagem": f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
