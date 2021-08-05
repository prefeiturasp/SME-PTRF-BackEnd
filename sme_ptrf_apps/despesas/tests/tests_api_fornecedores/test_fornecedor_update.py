import json
import pytest
from rest_framework import status
from ...models import Fornecedor

pytestmark = pytest.mark.django_db


def teste_api_fornecedor_update(jwt_authenticated_client, fornecedor_jose):

    fornecedor = Fornecedor.objects.filter(uuid=fornecedor_jose.uuid)

    assert fornecedor.exists()

    payload = {
        'nome': 'Nome Fornecedor José ALTERADO'
    }

    response = jwt_authenticated_client.patch(
        f'/api/fornecedores/{fornecedor_jose.id}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert Fornecedor.objects.get(uuid=fornecedor_jose.uuid).nome == payload['nome']

