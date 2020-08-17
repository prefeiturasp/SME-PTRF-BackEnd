import json

import pytest
from rest_framework import status

from sme_ptrf_apps.dre.models import TecnicoDre

pytestmark = pytest.mark.django_db

@pytest.fixture
def payload_tecnico_dre(dre_butantan):
    payload = {
        'dre': f'{dre_butantan.uuid}',
        'rf': '1234567',
        'nome': 'Pedro Antunes'
    }
    return payload


def test_create_tecnico_dre(jwt_authenticated_client, dre, payload_tecnico_dre):
    response = jwt_authenticated_client.post(
        '/api/tecnicos-dre/', data=json.dumps(payload_tecnico_dre), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert TecnicoDre.objects.filter(uuid=result['uuid']).exists()
