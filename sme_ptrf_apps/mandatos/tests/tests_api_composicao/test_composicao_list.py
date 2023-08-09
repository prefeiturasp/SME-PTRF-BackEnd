import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_get_composicoes(
    composicao_01_2023_a_2025,
    composicao_02_2023_a_2025,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/composicoes/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    # ['results'] por causa da paginação na viewset
    assert len(result['results']) == 2


def teste_get_composicao(
    composicao_01_2023_a_2025,
    composicao_02_2023_a_2025,
    jwt_authenticated_client_sme,
):
    response = jwt_authenticated_client_sme.get(
        f'/api/composicoes/{composicao_01_2023_a_2025.uuid}/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['data_inicial'] == '2023-01-01'
    assert result['data_final'] == '2025-12-31'
