import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_resource_url(jwt_authenticated_client, associacao):
    response = jwt_authenticated_client.get(f'/api/periodos/')
    assert response.status_code == status.HTTP_200_OK


def test_resource_lookup_url(jwt_authenticated_client, associacao):
    response = jwt_authenticated_client.get(f'/api/periodos/lookup/')
    assert response.status_code == status.HTTP_200_OK
