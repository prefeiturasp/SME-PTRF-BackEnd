import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload_update_acao_associacao(acao_associacao_charli_bravo_000086_x, acao_y):
    payload = {
        'acao': f'{acao_y.uuid}',
        'status': AcaoAssociacao.STATUS_INATIVA,
    }
    return payload


def test_update_acao_associacao(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x,
    payload_update_acao_associacao,
    acao_y
):

    response = jwt_authenticated_client_a.put(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/',
        data=json.dumps(payload_update_acao_associacao),
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    assert AcaoAssociacao.objects.filter(uuid=result['uuid']).exists()

    acao_associacao = AcaoAssociacao.objects.filter(uuid=result['uuid']).get()

    assert acao_associacao.acao == acao_y, "Deve atualizar a ação."
    assert acao_associacao.status == AcaoAssociacao.STATUS_INATIVA, "Deve atualizar o status."
