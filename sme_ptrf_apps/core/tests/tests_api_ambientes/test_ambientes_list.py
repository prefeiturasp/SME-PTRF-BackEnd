import json
import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def ambiente_dev():
    return baker.make(
        'Ambiente',
        prefixo='dev',
        nome='Desenvolvimento'
    )


@pytest.fixture
def ambiente_hom():
    return baker.make(
        'Ambiente',
        prefixo='hom',
        nome='Homologação'
    )


def test_api_ambientes_list(jwt_authenticated_client_a, ambiente_dev, ambiente_hom):
    response = jwt_authenticated_client_a.get(f'/api/ambientes/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': ambiente_dev.id,
            'prefixo': 'dev',
            'nome': 'Desenvolvimento'
        },
        {
            'id': ambiente_hom.id,
            'prefixo': 'hom',
            'nome': 'Homologação'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
