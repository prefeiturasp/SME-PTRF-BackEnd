import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_acao(
    jwt_authenticated_client_a,
    acao_x,
    acao_y
):
    response = jwt_authenticated_client_a.get(
        f'/api/acoes/{acao_x.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "uuid": f'{acao_x.uuid}',
        "id": acao_x.id,
        "nome": acao_x.nome,
        "e_recursos_proprios": acao_x.e_recursos_proprios,
        "posicao_nas_pesquisas": "ZZZZZZZZZZ",
        "aceita_capital": acao_x.aceita_capital,
        "aceita_custeio": acao_x.aceita_custeio,
        "aceita_livre": acao_x.aceita_livre
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado
