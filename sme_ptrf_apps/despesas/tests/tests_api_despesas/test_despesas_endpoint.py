import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/api/despesas/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_url_tabelas(associacao, jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/despesas/tabelas/')
    result = json.loads(response.content)

    chaves_esperadas = [
        'tipos_aplicacao_recurso',
        'tipos_custeio',
        'tipos_documento',
        'tipos_transacao',
        'acoes_associacao',
        'contas_associacao',
        'tags',
    ]
    assert response.status_code == status.HTTP_200_OK
    assert [key for key in result.keys()] == chaves_esperadas
