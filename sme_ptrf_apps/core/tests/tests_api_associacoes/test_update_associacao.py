import json

import pytest
from rest_framework import status

from ...models import Associacao

pytestmark = pytest.mark.django_db


def test_api_update_associacao(jwt_authenticated_client_a, associacao):
    payload = {
        "nome": "Nome alterado",
        "processo_regularidade": "123456"
    }
    response = jwt_authenticated_client_a.put(f'/api/associacoes/{associacao.uuid}/', data=json.dumps(payload),
                          content_type='application/json')

    registro_alterado = Associacao.objects.get(uuid=associacao.uuid)

    assert response.status_code == status.HTTP_200_OK
    assert registro_alterado.nome == 'Nome alterado'
    assert registro_alterado.processo_regularidade == '123456'
