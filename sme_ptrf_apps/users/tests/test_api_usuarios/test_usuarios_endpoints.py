import pytest

from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


def test_usuarios_endpoint(
    jwt_authenticated_client_u,
):
    with override_flag('gestao-usuarios', active=True):
        response = jwt_authenticated_client_u.get('/api/usuarios-v2/', content_type='application/json')
        assert response.status_code == status.HTTP_200_OK
        
    with override_flag('gestao-usuarios', active=False):
        response = jwt_authenticated_client_u.get('/api/usuarios-v2/', content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
