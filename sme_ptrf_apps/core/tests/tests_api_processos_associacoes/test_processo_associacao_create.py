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


def test_create_processo_associacao_servidor(jwt_authenticated_client_a, associacao, payload_processo_associacao):
    response = jwt_authenticated_client_a.post(
        '/api/processos-associacao/', data=json.dumps(payload_processo_associacao), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert ProcessoAssociacao.objects.filter(uuid=result['uuid']).exists()
