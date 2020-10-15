import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_devolucao_ao_tesouro():
    return baker.make('TipoDevolucaoAoTesouro', nome='Teste')


def test_api_list_devolucoes_ao_tesouro(jwt_authenticated_client, tipo_devolucao_ao_tesouro):
    response = jwt_authenticated_client.get(f'/api/tipos-devolucao-ao-tesouro/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_devolucao_ao_tesouro.id,
            'nome': 'Teste'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
