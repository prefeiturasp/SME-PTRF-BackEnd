import json

import pytest

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_conta():
    return baker.make('TipoConta', nome='Teste')


def test_api_list_tipos_conta(jwt_authenticated_client_a, tipo_conta):
    response = jwt_authenticated_client_a.get(f'/api/tipos-conta/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_conta.id,
            'nome': 'Teste',
            'apenas_leitura': tipo_conta.apenas_leitura,
            'uuid': f'{tipo_conta.uuid}'

        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
