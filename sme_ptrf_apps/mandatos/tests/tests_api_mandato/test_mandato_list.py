import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_get_mandatos(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


def teste_get_mandato(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/{mandato_01_2021_a_2022_api.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['referencia_mandato'] == '2021 a 2022'


def teste_get_mandatos_filtros(
    mandato_01_2021_a_2022_api,
    mandato_02_2023_a_2025_api,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/mandatos/?referencia=2023',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result['results']) == 1
