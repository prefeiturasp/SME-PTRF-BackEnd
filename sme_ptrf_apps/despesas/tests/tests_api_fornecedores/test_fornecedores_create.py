import json
import pytest
from rest_framework import status
from ...models import Fornecedor

pytestmark = pytest.mark.django_db


def test_api_create_fornecedor_cnpj(jwt_authenticated_client):

    payload = {
        'cpf_cnpj': '27.123.776/0001-55',
        'nome': 'Fornecedor teste CNPJ'
    }

    response = jwt_authenticated_client.post(
        f'/api/fornecedores/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Fornecedor.objects.filter(uuid=result['uuid']).exists()


def test_create_fornecedor_ja_existe(jwt_authenticated_client, fornecedor_jose):
    payload = {
        'cpf_cnpj': fornecedor_jose.cpf_cnpj,
        'nome': fornecedor_jose.nome
    }

    response = jwt_authenticated_client.post(
        f'/api/fornecedores/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == {
        "cpf_cnpj": [
            "Fornecedor with this CPF / CNPJ already exists."
        ]
    }
