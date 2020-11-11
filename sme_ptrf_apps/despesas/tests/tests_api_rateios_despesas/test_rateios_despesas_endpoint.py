import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_endpoint(associacao, jwt_authenticated_client_d):
    response = jwt_authenticated_client_d.get(f'/api/rateios-despesas/?associacao_uuid={associacao.uuid}')
    assert response.status_code == status.HTTP_200_OK
