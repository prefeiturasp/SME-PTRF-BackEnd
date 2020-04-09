import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_fornecedores(client, fornecedor_jose, fornecedor_industrias_teste):
    response = client.get(f'/api/fornecedores/', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_api_get_fornecedor_pelo_cpf(client, fornecedor_jose, fornecedor_industrias_teste):
    response = client.get(f'/api/fornecedores/?cpf_cnpj={fornecedor_jose.cpf_cnpj}', content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1


def test_api_get_fornecedor_pelo_cnpj(client, fornecedor_jose, fornecedor_industrias_teste):
    response = client.get(f'/api/fornecedores/?cpf_cnpj={fornecedor_industrias_teste.cpf_cnpj}',
                          content_type='application/json')
    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert len(result) == 1
