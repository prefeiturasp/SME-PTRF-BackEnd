import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_api_tabelas(jwt_authenticated_client_a):
    response = jwt_authenticated_client_a.get(f'/api/tipos-acerto-lancamento/tabelas/', content_type='application/json')
    assert response.status_code == status.HTTP_200_OK
