import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_resource_por_conta_e_periodo_url(authenticated_client, prestacao_conta):
    response = authenticated_client.get(f'/api/prestacoes-contas/por-conta-e-periodo/')
    assert response.status_code == status.HTTP_200_OK


def test_iniciar_prestacao_conta_url(authenticated_client, periodo, conta_associacao):
    conta_associacao_uuid = conta_associacao.uuid
    periodo_uuid = periodo.uuid

    response = authenticated_client.post(
        f'/api/prestacoes-contas/iniciar/?conta_associacao_uuid={conta_associacao_uuid}&periodo_uuid={periodo_uuid}')
    assert response.status_code != status.HTTP_404_NOT_FOUND


def test_revisar_prestacao_conta_url(authenticated_client, prestacao_conta):

    response = authenticated_client.patch(
        f'/api/prestacoes-contas/{prestacao_conta.uuid}/revisar/')
    assert response.status_code != status.HTTP_404_NOT_FOUND

def test_salvar_prestacao_conta_url(authenticated_client, prestacao_conta_iniciada):

    response = authenticated_client.patch(
        f'/api/prestacoes-contas/{prestacao_conta_iniciada.uuid}/salvar/')
    assert response.status_code != status.HTTP_404_NOT_FOUND
