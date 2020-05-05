import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_resource_por_conta_e_periodo_url(authenticated_client, prestacao_conta):
    response = authenticated_client.get(f'/api/prestacoes-contas/por-conta-e-periodo/')
    assert response.status_code == status.HTTP_200_OK
