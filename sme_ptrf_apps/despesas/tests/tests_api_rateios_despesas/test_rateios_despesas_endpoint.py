import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_endpoint(associacao, jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/rateios-despesas/')
    assert response.status_code == status.HTTP_200_OK
