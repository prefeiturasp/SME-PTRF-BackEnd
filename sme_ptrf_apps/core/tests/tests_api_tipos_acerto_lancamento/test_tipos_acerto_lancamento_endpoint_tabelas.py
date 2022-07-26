import json

import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import TipoAcertoLancamento
from sme_ptrf_apps.utils.choices_to_json import choices_to_json

pytestmark = pytest.mark.django_db


def test_api_list_choices(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-lancamento/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        "categorias": choices_to_json(TipoAcertoLancamento.CATEGORIA_CHOICES)
    }

    assert result == resultado_esperado
    assert response.status_code == status.HTTP_200_OK

