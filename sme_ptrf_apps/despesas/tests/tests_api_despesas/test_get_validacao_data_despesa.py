import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_get_validacao_data_despesa(jwt_authenticated_client_d, associacao):
    response = jwt_authenticated_client_d.get(f'/api/despesas/validar-data-da-despesa/?associacao_uuid={associacao.uuid}&data=2023-04-26')

    assert response.status_code == status.HTTP_200_OK

