import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_resource_por_associacao_e_periodo_url(jwt_authenticated_client_a, prestacao_conta):
    response = jwt_authenticated_client_a.get(f'/api/prestacoes-contas/por-associacao-e-periodo/')
    assert response.status_code == status.HTTP_200_OK


def test_concluir_prestacao_conta_url(jwt_authenticated_client_a, periodo, conta_associacao):
    conta_associacao_uuid = conta_associacao.uuid
    periodo_uuid = periodo.uuid

    response = jwt_authenticated_client_a.post(
        f'/api/prestacoes-contas/concluir/?conta_associacao_uuid={conta_associacao_uuid}&periodo_uuid={periodo_uuid}')
    assert response.status_code != status.HTTP_404_NOT_FOUND


def test_revisar_prestacao_conta_url(jwt_authenticated_client_a, prestacao_conta):

    response = jwt_authenticated_client_a.post(
        f'/api/prestacoes-contas/{prestacao_conta.uuid}/reabrir/')
    assert response.status_code != status.HTTP_404_NOT_FOUND
