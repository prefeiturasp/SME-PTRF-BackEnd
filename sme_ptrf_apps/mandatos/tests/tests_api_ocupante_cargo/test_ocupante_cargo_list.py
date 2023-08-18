import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_get_ocupantes_cargos(
    ocupante_cargo_01,
    ocupante_cargo_02,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/ocupantes-cargos/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


def teste_get_ocupante_cargo(
    ocupante_cargo_01,
    ocupante_cargo_02,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/ocupantes-cargos/{ocupante_cargo_01.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['cargo_educacao'] == 'Diretor de Escola'
    assert result['representacao'] == 'Servidor'
