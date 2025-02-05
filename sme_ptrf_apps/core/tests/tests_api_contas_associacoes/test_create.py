import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import ContaAssociacao

pytestmark = pytest.mark.django_db


def test_create_tipo_acerto_documento(
        jwt_authenticated_client_a,
        associacao_1,
        tipo_conta_1):
    payload_nova_conta_associacao = {
        "tipo_conta": str(tipo_conta_1.uuid),
        "status": "ATIVA",
        "associacao": str(associacao_1.uuid),
        "banco_nome": "banco do brasil",
        "agencia": "0001"
    }

    response = jwt_authenticated_client_a.post(
        f'/api/contas-associacoes/', data=json.dumps(payload_nova_conta_associacao),
        content_type='application/json'
    )

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert ContaAssociacao.objects.filter(uuid=result['uuid']).exists()
