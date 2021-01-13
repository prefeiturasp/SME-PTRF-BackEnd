import json

import pytest

from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def acao_x():
    return baker.make('Acao', nome='X')


@pytest.fixture
def acao_y():
    return baker.make('Acao', nome='Y')


def test_api_acoes_list(jwt_authenticated_client_a, acao_x, acao_y):
    response = jwt_authenticated_client_a.get(f'/api/acoes/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': acao_x.id,
            'nome': 'X',
            'uuid': f'{acao_x.uuid}',
            'e_recursos_proprios': False
        },
        {
            'id': acao_y.id,
            'nome': 'Y',
            'uuid': f'{acao_y.uuid}',
            'e_recursos_proprios': False
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
