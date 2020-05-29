import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_authorized(authenticated_client):
    response = authenticated_client.get('/api/despesas/')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_url_tabelas(associacao, jwt_authenticated_client):
    response = jwt_authenticated_client.get('/api/despesas/tabelas/')
    assert response.status_code == status.HTTP_200_OK
