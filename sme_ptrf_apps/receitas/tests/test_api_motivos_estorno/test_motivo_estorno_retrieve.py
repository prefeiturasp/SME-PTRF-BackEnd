import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_motivo_estorno(jwt_authenticated_client_p, motivo_estorno_01):
    response = jwt_authenticated_client_p.get(
        f'/api/motivos-estorno/{motivo_estorno_01.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        'id': motivo_estorno_01.id,
        'uuid': f'{motivo_estorno_01.uuid}',
        'motivo': 'Motivo de estorno 01'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


