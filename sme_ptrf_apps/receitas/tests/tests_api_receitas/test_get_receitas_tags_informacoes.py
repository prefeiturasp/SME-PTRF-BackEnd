import json

import pytest
from rest_framework import status
from sme_ptrf_apps.receitas.models import Receita


pytestmark = pytest.mark.django_db


def test_api_get_receita_tabelas(jwt_authenticated_client_p):

    response = jwt_authenticated_client_p.get(f'/api/receitas/tags-informacoes/', content_type='application/json')
    result = json.loads(response.content)

    esperado = Receita.get_tags_informacoes_list()

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
