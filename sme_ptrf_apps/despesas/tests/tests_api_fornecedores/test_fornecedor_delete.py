import pytest
from rest_framework import status
from ...models import Fornecedor

pytestmark = pytest.mark.django_db


def teste_api_fornecedor_delete(jwt_authenticated_client, fornecedor_jose):

    assert Fornecedor.objects.filter(id=fornecedor_jose.id).exists()

    response = jwt_authenticated_client.delete(
        f'/api/fornecedores/{fornecedor_jose.id}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Fornecedor.objects.filter(id=fornecedor_jose.id).exists()

