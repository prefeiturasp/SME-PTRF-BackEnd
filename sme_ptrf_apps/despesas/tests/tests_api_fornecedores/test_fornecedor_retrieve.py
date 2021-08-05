import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def teste_api_fornecedor_retrieve(jwt_authenticated_client, fornecedor_jose):
    response = jwt_authenticated_client.get(f'/api/fornecedores/{fornecedor_jose.id}/', content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
            "id": fornecedor_jose.id,
            "criado_em": fornecedor_jose.criado_em.isoformat("T"),
            "alterado_em": fornecedor_jose.alterado_em.isoformat("T"),
            "uuid": f'{fornecedor_jose.uuid}',
            "cpf_cnpj": fornecedor_jose.cpf_cnpj,
            "nome": fornecedor_jose.nome
        }

    assert response.status_code == status.HTTP_200_OK
    assert result == resultado_esperado
