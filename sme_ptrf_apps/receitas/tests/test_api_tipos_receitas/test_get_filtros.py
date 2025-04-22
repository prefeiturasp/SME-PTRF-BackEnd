
import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_filtros(jwt_authenticated_client_sme, detalhe_tipo_receita):
    response = jwt_authenticated_client_sme.get(f'/api/tipos-receitas/filtros/', content_type='application/json')
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(content["tipos_contas"]) == 1
    assert len(content["tipos"]) == 4
    assert len(content["aceita"]) == 3
    assert len(content["detalhes"]) == 1
