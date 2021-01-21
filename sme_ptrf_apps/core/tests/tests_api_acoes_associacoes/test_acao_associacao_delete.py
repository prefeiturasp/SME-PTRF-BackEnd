import json

import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import AcaoAssociacao

pytestmark = pytest.mark.django_db


def test_delete_acao_associacao(
    jwt_authenticated_client_a,
    acao_associacao_charli_bravo_000086_x
):
    assert AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes-associacoes/{acao_associacao_charli_bravo_000086_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not AcaoAssociacao.objects.filter(uuid=acao_associacao_charli_bravo_000086_x.uuid).exists()


def test_delete_acao_associacao_ja_usada(
    jwt_authenticated_client_a,
    acao_associacao_eco_delta_000087_x,
    receita_usando_acao_associacao_eco_delta_x
):

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes-associacoes/{acao_associacao_eco_delta_000087_x.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "erro": 'ProtectedError',
        "mensagem": "Essa ação de associação não pode ser excluida porque está sendo usada na aplicação.",
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
