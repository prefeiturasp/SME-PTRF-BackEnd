import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_anos_analise_regularidade(
    jwt_authenticated_client_dre,
    ano_analise_regularidade_2020,
    ano_analise_regularidade_2021
):
    response = jwt_authenticated_client_dre.get(f'/api/anos-analise-regularidade/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {"ano": 2021},
        {"ano": 2020},
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
