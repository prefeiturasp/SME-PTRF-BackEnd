import json
import pytest
from rest_framework import status

from sme_ptrf_apps.core.models import Acao

pytestmark = pytest.mark.django_db


def test_delete_acao(
    jwt_authenticated_client_a,
    acao_x
):
    assert Acao.objects.filter(uuid=acao_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes/{acao_x.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Acao.objects.filter(uuid=acao_x.uuid).exists()


def test_delete_acao_ja_usada(
    jwt_authenticated_client_a,
    acao_x,
    acao_associacao_eco_delta_000087_x
):
    assert Acao.objects.filter(uuid=acao_x.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/acoes/{acao_x.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "erro": 'ProtectedError',
        "mensagem": 'Essa operação não pode ser realizada. Há associações vinculadas a esse tipo de ação.',
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado
