import json

import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


def test_get_parametro_mes(jwt_authenticated_client_sme, flag_paa, parametro_paa):
    response = jwt_authenticated_client_sme.get('/api/parametros-paa/mes-elaboracao-paa/')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert 'detail' in content
    assert content['detail'] == parametro_paa.mes_elaboracao_paa

