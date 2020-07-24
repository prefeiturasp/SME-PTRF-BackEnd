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
    payload_despesa_valida
):
    response = client.post('/api/despesas/', data=json.dumps(payload_despesa_valida), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
    assert despesa.documento_transacao == '123456789'



def test_api_post_despesas_com_rateio_com_tag(
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
    tag_ativa,
    payload_despesa_valida_rateio_com_tag
):
    response = client.post('/api/despesas/', data=json.dumps(payload_despesa_valida_rateio_com_tag), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
    assert despesa.documento_transacao == '123456789'
