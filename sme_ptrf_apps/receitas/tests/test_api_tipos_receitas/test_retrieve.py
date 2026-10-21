import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_sucesso(jwt_authenticated_client_p, tipo_receita_estorno):
    response = jwt_authenticated_client_p.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/',
        content_type='application/json',
    )
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['uuid'] == str(tipo_receita_estorno.uuid)
    assert content['nome'] == tipo_receita_estorno.nome


def test_retrieve_uuid_invalido(jwt_authenticated_client_p):
    response = jwt_authenticated_client_p.get(
        '/api/tipos-receitas/00000000-0000-0000-0000-000000000000/',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_retrieve_nao_autenticado(client, tipo_receita_estorno):
    response = client.get(
        f'/api/tipos-receitas/{tipo_receita_estorno.uuid}/',
        content_type='application/json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
