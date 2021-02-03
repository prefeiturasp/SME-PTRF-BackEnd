import json
import pytest


from rest_framework import status

from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_update_acao(acao_x):
    payload = {
        'nome': 'x alterada',
    }
    return payload


def test_update_acao(
    jwt_authenticated_client_a,
    acao_x,
    payload_update_acao
):

    assert Acao.objects.get(uuid=acao_x.uuid).nome == 'X'

    response = jwt_authenticated_client_a.patch(
        f'/api/acoes/{acao_x.uuid}/',
        data=json.dumps(payload_update_acao),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert Acao.objects.get(uuid=acao_x.uuid).nome == 'x alterada'
