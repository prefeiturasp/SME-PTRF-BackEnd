import json
import pytest

from rest_framework import status


from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_acao_nova():
    payload = {
        'nome': 'Nova',
        'e_recursos_proprios': False,
    }
    return payload


def test_create_acao(
    jwt_authenticated_client_a,
    payload_acao_nova
):
    response = jwt_authenticated_client_a.post(
        '/api/acoes/', data=json.dumps(payload_acao_nova), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Acao.objects.filter(uuid=result['uuid']).exists()
