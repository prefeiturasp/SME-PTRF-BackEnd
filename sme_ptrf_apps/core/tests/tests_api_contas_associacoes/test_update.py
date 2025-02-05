import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import ContaAssociacao

pytestmark = pytest.mark.django_db


def test_update_conta_associacao(
    jwt_authenticated_client_a,
    conta_associacao_1
):

    payload = {
        'banco_nome': 'Banco UCM',
    }

    response = jwt_authenticated_client_a.patch(
        f'/api/contas-associacoes/{str(conta_associacao_1.uuid)}/',
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert ContaAssociacao.objects.get(uuid=conta_associacao_1.uuid).banco_nome == "Banco UCM"
