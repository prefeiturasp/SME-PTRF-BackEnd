import json

import pytest
from rest_framework import status

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_api_post_despesas(
    client,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    despesa,
    rateio_despesa_capital,
    payload_despesa_valida
):
    response = client.put(f'/api/despesas/{despesa.uuid}/', data=json.dumps(payload_despesa_valida),
                          content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.cpf_cnpj_fornecedor == payload_despesa_valida['cpf_cnpj_fornecedor']
