import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_cargos_diretoria_executiva(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/membros-associacao/cargos-diretoria-executiva/', content_type='application/json')
    result = json.loads(response.content)

    expected_results = [
        {
            "id": "PRESIDENTE_DIRETORIA_EXECUTIVA",
            "nome": "Presidente da diretoria executiva"
        },
        {
            "id": "VICE_PRESIDENTE_DIRETORIA_EXECUTIVA",
            "nome": "Vice-Presidente da diretoria executiva"
        },
        {
            "id": "SECRETARIO",
            "nome": "Secretario"
        },
        {
            "id": "TESOUREIRO",
            "nome": "Tesoureiro"
        },
        {
            "id": "VOGAL_1",
            "nome": "Vogal 1"
        },
        {
            "id": "VOGAL_2",
            "nome": "Vogal 2"
        },
        {
            "id": "VOGAL_3",
            "nome": "Vogal 3"
        },
        {
            "id": "VOGAL_4",
            "nome": "Vogal 4"
        },
        {
            "id": "VOGAL_5",
            "nome": "Vogal 5"
        }
    ]
    assert response.status_code == status.HTTP_200_OK
    assert result == expected_results

