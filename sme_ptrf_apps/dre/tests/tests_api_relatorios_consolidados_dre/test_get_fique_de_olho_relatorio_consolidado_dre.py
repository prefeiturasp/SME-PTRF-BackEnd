import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_status_relatorio_analise_completa_rel_nao_gerado(jwt_authenticated_client_relatorio_consolidado, parametros):
    response = jwt_authenticated_client_relatorio_consolidado.get(
        f'/api/relatorios-consolidados-dre/fique-de-olho/',
        content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {'detail': ''}

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado

