import pytest
from rest_framework import status
import json

from ...models import Associacao

from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_api_delete_associacao(jwt_authenticated_client_a, associacao):

    assert Associacao.objects.filter(uuid=associacao.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/associacoes/{associacao.uuid}/', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Associacao.objects.filter(uuid=associacao.uuid).exists()


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
        'mensagem': 'Essa associação não pode ser excluída porque está sendo usada na aplicação.'
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == esperado



