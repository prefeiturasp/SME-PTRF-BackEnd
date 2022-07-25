import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_retrieve_tipo_acerto_lancamento(jwt_authenticated_client_a, tipo_acerto_lancamento_retrieve):
    response = jwt_authenticated_client_a.get(
        f'/api/tipos-acerto-lancamento/{tipo_acerto_lancamento_retrieve.uuid}/',
        content_type='applicaton/json'
    )

    result = json.loads(response.content)
    resultado_esperado = {
        'id': tipo_acerto_lancamento_retrieve.id,
        'nome': "Teste retrieve",
        'categoria': "DEVOLUCAO",
        'ativo': True,
        'uuid': f'{tipo_acerto_lancamento_retrieve.uuid}'
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado


