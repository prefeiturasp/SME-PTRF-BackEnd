import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_url_retrieve(authenticated_client, associacao):
    response = authenticated_client.get(f'/api/associacoes/{associacao.uuid}/')
    assert response.status_code == status.HTTP_200_OK
