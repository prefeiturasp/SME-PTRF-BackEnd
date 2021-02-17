import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_tipos_custeio_list(jwt_authenticated_client_d, tipo_custeio_01, tipo_custeio_02):
    response = jwt_authenticated_client_d.get(f'/api/tipos-custeio/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = [
        {
            'nome': tipo_custeio_01.nome,
            'id': tipo_custeio_01.id,
            'uuid': f'{tipo_custeio_01.uuid}'
        },
        {
            'nome': tipo_custeio_02.nome,
            'id': tipo_custeio_02.id,
            'uuid': f'{tipo_custeio_02.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
