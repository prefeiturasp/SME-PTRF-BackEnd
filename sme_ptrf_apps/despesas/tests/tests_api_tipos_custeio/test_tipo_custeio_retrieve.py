import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_tipo_custeio(jwt_authenticated_client_d, tipo_custeio_01):
    response = jwt_authenticated_client_d.get(
        f'/api/tipos-custeio/{tipo_custeio_01.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)

    resultado_esperado = {
        'eh_tributos_e_tarifas': False,
        'nome': tipo_custeio_01.nome,
        'id': tipo_custeio_01.id,
        'uuid': f'{tipo_custeio_01.uuid}',
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
