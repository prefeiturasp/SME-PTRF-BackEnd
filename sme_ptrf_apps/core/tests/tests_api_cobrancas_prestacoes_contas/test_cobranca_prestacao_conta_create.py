import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import CobrancaPrestacaoConta

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_cobranca(prestacao_conta_2020_1_conciliada):
    payload = {
        'prestacao_conta': f'{prestacao_conta_2020_1_conciliada.uuid}',
        'data': "2020-10-10",
        'tipo': 'RECEBIMENTO'
    }
    return payload


def test_create_cobranca_prestacao_conta(client, associacao, payload_cobranca):
    response = client.post(
        '/api/cobrancas-prestacoes-contas/', data=json.dumps(payload_cobranca), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert CobrancaPrestacaoConta.objects.filter(uuid=result['uuid']).exists()
