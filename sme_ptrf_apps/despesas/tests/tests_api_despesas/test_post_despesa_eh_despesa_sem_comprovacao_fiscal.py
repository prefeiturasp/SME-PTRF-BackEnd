import json

import pytest
from rest_framework import status

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_status_incompleto_eh_despesa_sem_comprovacao_fiscal(
    jwt_authenticated_client_d,
    associacao,
    payload_despesa_status_incompleto_eh_despesa_sem_comprovacao_fiscal
):
    from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_INCOMPLETO

    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_status_incompleto_eh_despesa_sem_comprovacao_fiscal),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
    assert despesa.status == STATUS_INCOMPLETO


def test_status_completo_eh_despesa_sem_comprovacao_fiscal(
    jwt_authenticated_client_d,
    associacao,
    conta_associacao,
    acao_associacao,
    payload_despesa_status_completo_eh_despesa_sem_comprovacao_fiscal
):
    from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO

    response = jwt_authenticated_client_d.post('/api/despesas/', data=json.dumps(payload_despesa_status_completo_eh_despesa_sem_comprovacao_fiscal),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Despesa.objects.filter(uuid=result["uuid"]).exists()

    despesa = Despesa.objects.get(uuid=result["uuid"])

    assert despesa.associacao.uuid == associacao.uuid
    assert despesa.status == STATUS_COMPLETO

