import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_search_receitas_por_nome(client, tipo_receita,
                                          receita_xxx, receita_yyy,
                                          acao,
                                          acao_associacao,
                                          associacao,
                                          tipo_conta,
                                          conta_associacao):
    response = client.get(f'/api/receitas/?associacao__uuid={associacao.uuid}&search=xxx',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
