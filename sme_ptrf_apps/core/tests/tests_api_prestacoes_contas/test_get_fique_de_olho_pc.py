import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_texto_fique_de_olho_pc(jwt_authenticated_client_a, parametro_fique_de_olho_pc_texto_abc):
    response = jwt_authenticated_client_a.get(
        f'/api/prestacoes-contas/fique-de-olho/',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {'detail': 'abc'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

