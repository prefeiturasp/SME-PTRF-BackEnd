import json

import pytest
from rest_framework import status

from ...models import PrestacaoConta

pytestmark = pytest.mark.django_db


def test_api_get_prestacoes_contas_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get('/api/prestacoes-contas/tabelas/', content_type='application/json')
    result = json.loads(response.content)
    esperado = {
        'status': PrestacaoConta.status_to_json(),
        'status_de_conclusao_de_pc': PrestacaoConta.status_conclusao_pc_to_json()
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
