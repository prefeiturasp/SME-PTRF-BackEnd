import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_usuarios_endpoint(
    jwt_authenticated_client_u,
):
    response = jwt_authenticated_client_u.get('/api/usuarios-v2/', content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
