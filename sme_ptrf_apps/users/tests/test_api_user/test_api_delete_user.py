import pytest

pytestmark = pytest.mark.django_db

def test_deletar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3
):

    from django.contrib.auth import get_user_model

    User = get_user_model()
    assert User.objects.filter(id=usuario_3.id).exists()

    jwt_authenticated_client_u.delete(f"/api/usuarios/{usuario_3.id}/", content_type='application/json')
    assert not User.objects.filter(id=usuario_3.id).exists()
