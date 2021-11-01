import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_motivos_todos(jwt_authenticated_client, motivo_reprovacao_x, motivo_reprovacao_y):
    response = jwt_authenticated_client.get(f'/api/motivos-reprovacao/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{motivo_reprovacao_x.uuid}',
            "motivo": f'{motivo_reprovacao_x.motivo}',
        },
        {
            "uuid": f'{motivo_reprovacao_y.uuid}',
            "motivo": f'{motivo_reprovacao_y.motivo}',
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
