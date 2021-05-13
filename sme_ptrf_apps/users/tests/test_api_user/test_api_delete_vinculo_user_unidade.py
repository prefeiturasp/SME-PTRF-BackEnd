import pytest

from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_delete_vinculo_usuario_unidade(
        jwt_authenticated_client_u,
        usuario_duas_unidades,
        unidade,
        unidade_diferente
):

    User = get_user_model()
    u = User.objects.filter(username=usuario_duas_unidades.username).first()
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade.codigo_eol, unidade_diferente.codigo_eol ]

    jwt_authenticated_client_u.delete(
        f"/api/usuarios/{usuario_duas_unidades.id}/unidades/{unidade.codigo_eol}/",
        content_type='application/json'
    )

    u = User.objects.filter(username=usuario_duas_unidades.username).first()
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade_diferente.codigo_eol, ]
