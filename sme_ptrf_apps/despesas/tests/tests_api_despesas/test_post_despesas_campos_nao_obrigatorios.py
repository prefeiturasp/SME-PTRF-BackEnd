import json

import pytest
from rest_framework import status

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_api_post_despesas_nao_obrigatorias_com_rateios(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_sem_campos_nao_obrigatorios
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_sem_campos_nao_obrigatorios),
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid


def test_api_post_despesas_nao_obrigatorias_sem_rateios(
    jwt_authenticated_client_d,
    tipo_aplicacao_recurso,
    tipo_custeio,
    tipo_documento,
    tipo_transacao,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_despesa_sem_campos_nao_obrigatorios_sem_rateios
):
    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_sem_campos_nao_obrigatorios_sem_rateios),
                           content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
