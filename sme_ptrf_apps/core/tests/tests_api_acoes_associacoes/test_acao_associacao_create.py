import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_acao_associacao(associacao_charli_bravo_000086, acao_x):
    payload = {
        'associacao': f'{associacao_charli_bravo_000086.uuid}',
        'acao': f'{acao_x.uuid}',
        'status': AcaoAssociacao.STATUS_ATIVA,
    }
    return payload


def test_create_acao_associacao(
    jwt_authenticated_client_a,
    associacao_charli_bravo_000086,
    acao_x,
    payload_acao_associacao
):
    response = jwt_authenticated_client_a.post(
        '/api/acoes-associacoes/', data=json.dumps(payload_acao_associacao), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert AcaoAssociacao.objects.filter(uuid=result['uuid']).exists()
