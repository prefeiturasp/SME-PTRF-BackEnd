import json
import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_get_conta_associacao_sucesso(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/{str(conta_associacao_1.uuid)}/',
        content_type='applicaton/json'
    )

    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["uuid"] == str(conta_associacao_1.uuid)


def test_get_conta_associacao_nao_encontrado(
    jwt_authenticated_client_a,
    conta_associacao_1
):
    response = jwt_authenticated_client_a.get(
        f'/api/contas-associacoes/59c8da98-90f1-4e20-8565-e530adddfa0a/',
        content_type='applicaton/json'
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
