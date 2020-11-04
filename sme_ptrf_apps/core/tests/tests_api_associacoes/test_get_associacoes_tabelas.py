import json

import pytest
from rest_framework import status

from ...models import Associacao, Unidade

pytestmark = pytest.mark.django_db


def test_api_get_associacoes_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/associacoes/tabelas/', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'tipos_unidade': Unidade.tipos_unidade_to_json(),
        'status_regularidade': Associacao.status_regularidade_to_json(),
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
