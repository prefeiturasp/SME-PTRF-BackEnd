import json
import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_encerrar_acesso_usuario_unidade(
        jwt_authenticated_client_u,
        usuario_3,
        dre,
):
    payload = {
        'unidade_suporte_uuid': f'{dre.uuid}'
    }

    response = jwt_authenticated_client_u.post(
        f"/api/usuarios/{usuario_3.username}/encerrar-acesso-suporte/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK


def test_encerrar_acesso_usuario_unidade_sem_passar_codigo_eol(
        jwt_authenticated_client_u,
        usuario_3,
):
    payload = {
    }

    response = jwt_authenticated_client_u.post(
        f"/api/usuarios/{usuario_3.username}/encerrar-acesso-suporte/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)
    assert result == "Campo 'codigo_eol' não encontrado no payload."

