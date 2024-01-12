import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.core.fixtures.factories import AcaoFactory, AcaoAssociacaoFactory, AssociacaoFactory

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


def test_validacao_update_acao_associacao(jwt_authenticated_client_a):
    associacao = AssociacaoFactory()
    acao = AcaoFactory()
    outra_acao = AcaoFactory()

    acao_associacao_existente = AcaoAssociacaoFactory(associacao=associacao, acao=acao)

    payload = {
        'acao': f"{outra_acao.uuid}",
        'associacao': f"{associacao.uuid}"
    }

    response = jwt_authenticated_client_a.put(
        f'/api/acoes-associacoes/{acao_associacao_existente.uuid}/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['acao'] == f"{outra_acao.uuid}"
