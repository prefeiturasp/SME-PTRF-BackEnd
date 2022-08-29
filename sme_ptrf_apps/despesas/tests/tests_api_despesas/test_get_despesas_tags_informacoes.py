import json

import pytest
from rest_framework import status

from sme_ptrf_apps.despesas.models import Despesa

pytestmark = pytest.mark.django_db


def test_api_get_despesas_tabelas(jwt_authenticated_client_d):

    response = jwt_authenticated_client_d.get(f'/api/despesas/tags-informacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = Despesa.get_tags_informacoes_list()

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
