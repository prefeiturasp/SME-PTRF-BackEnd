import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_status_consolidado_dre(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/status-consolidado-dre/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_200_OK


def test_get_status_consolidado_dre_erro_sem_dre(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/status-consolidado-dre/?periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        "erro": "parametros_requeridos",
        "mensagem": "É necessário enviar os uuids da dre e período"
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_status_consolidado_dre_erro_sem_periodo(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/status-consolidado-dre/?dre={dre_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        "erro": "parametros_requeridos",
        "mensagem": "É necessário enviar os uuids da dre e período"
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_status_consolidado_dre_erro_dre_uuid_false(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    dre_uuid = f"{dre_teste_api_consolidado_dre.uuid}X"  # Uuid inválido
    periodo_uuid = periodo_teste_api_consolidado_dre.uuid

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/status-consolidado-dre/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        "erro": "Objeto não encontrado.",
        "mensagem": f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_status_consolidado_dre_erro_periodo_uuid_false(
    jwt_authenticated_client_dre,
    dre_teste_api_consolidado_dre,
    periodo_teste_api_consolidado_dre,
    consolidado_dre_teste_api_consolidado_dre,
):
    dre_uuid = dre_teste_api_consolidado_dre.uuid
    periodo_uuid = f"{periodo_teste_api_consolidado_dre.uuid}X" # Uuid inválido

    response = jwt_authenticated_client_dre.get(
        f'/api/consolidados-dre/status-consolidado-dre/?dre={dre_uuid}&periodo={periodo_uuid}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        "erro": "Objeto não encontrado.",
        "mensagem": f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
