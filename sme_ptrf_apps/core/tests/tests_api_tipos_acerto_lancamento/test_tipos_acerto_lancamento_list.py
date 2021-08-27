import json

import pytest
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_acerto_lancamento():
    return baker.make('TipoAcertoLancamento', nome='Teste', categoria='BASICO')


def test_api_list_tipos_acerto_lancamento(jwt_authenticated_client_a, tipo_acerto_lancamento):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-lancamento/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': tipo_acerto_lancamento.id,
            'nome': 'Teste',
            'categoria': 'BASICO',
            'uuid': f'{tipo_acerto_lancamento.uuid}'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
