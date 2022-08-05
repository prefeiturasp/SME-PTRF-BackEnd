import json
import pytest

from django.contrib.auth import get_user_model

from rest_framework import status

from ...models import UnidadeEmSuporte

pytestmark = pytest.mark.django_db


def test_viabiizar_acesso_usuario_unidade(
        jwt_authenticated_client_u,
        usuario_3,
        unidade,
        unidade_diferente
):
    payload = {
        'codigo_eol': unidade_diferente.codigo_eol
    }

    User = get_user_model()
    u = User.objects.filter(username=usuario_3.username).first()
    assert list(u.unidades.values_list('codigo_eol', flat=True)) == [unidade.codigo_eol, ]

    response = jwt_authenticated_client_u.post(
        f"/api/usuarios/{usuario_3.username}/viabilizar-acesso-suporte/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert UnidadeEmSuporte.objects.filter(user=usuario_3).exists(), "Deveria ter sido registrado o acesso de suporte."


def test_viabiizar_acesso_usuario_unidade_sem_passar_codigo_eol(
        jwt_authenticated_client_u,
        usuario_3,
        unidade,
        unidade_diferente
):
    payload = {
    }

    response = jwt_authenticated_client_u.post(
        f"/api/usuarios/{usuario_3.username}/viabilizar-acesso-suporte/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)
    assert result == "Campo 'codigo_eol' não encontrado no payload."

