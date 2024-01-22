import json
import pytest

from rest_framework import status

from sme_ptrf_apps.users.fixtures.factories.usuario_factory import UsuarioFactory
from sme_ptrf_apps.users.fixtures.factories.unidade_em_suporte_factory import UnidadeEmSuporteFactory

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
    assert result == "Campo 'unidade_suporte_uuid' não encontrado no payload."


def test_encerrar_acesso_usuario_unidade_em_lote(jwt_authenticated_client_u):
    usuario = UsuarioFactory()

    unidades = []
    for _ in range(10):
        suporte = UnidadeEmSuporteFactory(user=usuario)
        unidades.append(f'{suporte.unidade.uuid}')

    payload = {
        'unidade_suporte_uuids': unidades
    }

    response = jwt_authenticated_client_u.post(
        f"/api/usuarios/{usuario.username}/encerrar-acesso-suporte-em-lote/",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert usuario.acessos_de_suporte.count() == 0
    assert response.status_code == status.HTTP_200_OK
