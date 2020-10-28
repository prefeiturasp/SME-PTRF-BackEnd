import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import ProcessoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_processo_associacao(associacao):
    payload = {
        'associacao': str(associacao.uuid),
        'numero_processo': "271170",
        'ano': '2020'
    }
    return payload


def test_update_processo_associacao(jwt_authenticated_client_a, associacao, processo_associacao_123456_2019,
                                    payload_processo_associacao):
    numero_processo_novo = "190889"
    payload_processo_associacao['numero_processo'] = numero_processo_novo
    response = jwt_authenticated_client_a.put(
        f'/api/processos-associacao/{processo_associacao_123456_2019.uuid}/',
        data=json.dumps(payload_processo_associacao),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert ProcessoAssociacao.objects.filter(uuid=result['uuid']).exists()

    processo = ProcessoAssociacao.objects.filter(uuid=result['uuid']).get()

    assert processo.numero_processo == numero_processo_novo
