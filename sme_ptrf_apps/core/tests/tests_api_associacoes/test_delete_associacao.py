import pytest
from rest_framework import status
import json

from ...models import Associacao

from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_api_delete_associacao(jwt_authenticated_client_a, associacao_d):

    assert Associacao.objects.filter(uuid=associacao_d.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/associacoes/{associacao_d.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Associacao.objects.filter(uuid=associacao_d.uuid).exists()


def test_api_delete_associacao_ja_usada(
    jwt_authenticated_client_a,
    associacao,
    ata_2020_1_cheque_aprovada
):

    response = jwt_authenticated_client_a.delete(
        f'/api/associacoes/{associacao.uuid}/', content_type='application/json')

    result = json.loads(response.content)

    esperado = {
        "erro": 'ProtectedError',
        'mensagem': 'Não é possível excluir essa associação porque ela já possui movimentação (despesas, receitas, etc.)'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado



