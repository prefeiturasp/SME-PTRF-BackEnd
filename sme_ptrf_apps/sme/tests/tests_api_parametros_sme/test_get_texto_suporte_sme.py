import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_texto_suporte_sme(jwt_authenticated_client_sme, parametros):
    response = jwt_authenticated_client_sme.get('/api/parametros-sme/texto-pagina-suporte/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {'detail': 'Teste SME'}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
