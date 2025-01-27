import json
import pytest
from rest_framework import status
from sme_ptrf_apps.core.models import ContaAssociacao

pytestmark = pytest.mark.django_db


def test_delete_conta_associacao(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    assert ContaAssociacao.objects.filter(uuid=conta_associacao_1.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/contas-associacoes/{str(conta_associacao_1.uuid)}/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not ContaAssociacao.objects.filter(uuid=conta_associacao_1.uuid).exists()


def test_delete_conta_associacao_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    assert ContaAssociacao.objects.filter(uuid=conta_associacao_1.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/contas-associacoes/59c8da98-90f1-4e20-8565-e530adddfa0a/',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_conta_associacao_error(
    jwt_authenticated_client_a,
    conta_associacao_1,
    demonstrativo_financeiro_factory

):
    demonstrativo_financeiro_factory.create(conta_associacao=conta_associacao_1)
    assert ContaAssociacao.objects.filter(uuid=conta_associacao_1.uuid).exists()

    response = jwt_authenticated_client_a.delete(
        f'/api/contas-associacoes/{str(conta_associacao_1.uuid)}/',
        content_type='application/json'
    )

    result = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == {
        'erro': 'ProtectedError',
        'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a essa ação da referida Conta Associação'
    }
    assert ContaAssociacao.objects.filter(uuid=conta_associacao_1.uuid).exists()
