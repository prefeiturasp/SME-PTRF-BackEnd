import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_list_motivo_estorno_por_nome(jwt_authenticated_client_p, motivo_estorno_01, motivo_estorno_02):
    response = jwt_authenticated_client_p.get(
        f'/api/motivos-estorno/?motivo=01',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': motivo_estorno_01.id,
            'uuid': f'{motivo_estorno_01.uuid}',
            'motivo': 'Motivo de estorno 01'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


def test_api_motivos_estorno_list(jwt_authenticated_client_p, motivo_estorno_01, motivo_estorno_02):
    response = jwt_authenticated_client_p.get(f'/api/motivos-estorno/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'id': motivo_estorno_01.id,
            'uuid': f'{motivo_estorno_01.uuid}',
            'motivo': 'Motivo de estorno 01'
        },
        {
            'id': motivo_estorno_02.id,
            'uuid': f'{motivo_estorno_02.uuid}',
            'motivo': 'Motivo de estorno 02'
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

