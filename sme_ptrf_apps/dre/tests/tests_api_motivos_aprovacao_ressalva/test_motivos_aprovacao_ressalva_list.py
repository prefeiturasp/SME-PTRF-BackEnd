import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_list_motivos_todos(jwt_authenticated_client, motivo_aprovacao_ressalva_x, motivo_aprovacao_ressalva_y):
    response = jwt_authenticated_client.get(f'/api/motivos-aprovacao-ressalva/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            "uuid": f'{motivo_aprovacao_ressalva_x.uuid}',
            "motivo": f'{motivo_aprovacao_ressalva_x.motivo}',
            "recurso": f'{motivo_aprovacao_ressalva_x.recurso.uuid}' if motivo_aprovacao_ressalva_x.recurso else None
        },
        {
            "uuid": f'{motivo_aprovacao_ressalva_y.uuid}',
            "motivo": f'{motivo_aprovacao_ressalva_y.motivo}',
            "recurso": f'{motivo_aprovacao_ressalva_y.recurso.uuid}' if motivo_aprovacao_ressalva_y.recurso else None
        }
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
