import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(jwt_authenticated_client_d):
    response = jwt_authenticated_client_d.get('/api/despesas/')
    assert response.status_code == status.HTTP_200_OK


def test_url_tabelas(associacao, jwt_authenticated_client_d):
    response = jwt_authenticated_client_d.get(f'/api/despesas/tabelas/?associacao_uuid={associacao.uuid}')
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
