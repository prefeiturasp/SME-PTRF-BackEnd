import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_action_usuarios_servidores_por_visao_nao_deve_passar_sem_visao(
    jwt_authenticated_client_u
):
    response = jwt_authenticated_client_u.get(
        f'/api/usuarios/usuarios-servidores-por-visao/',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametros_requerido',
        'mensagem': 'É necessário o parametro ?visao='
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_usuarios_servidores_por_visao_nao_deve_passar_visao_inexistente(
    jwt_authenticated_client_u
):
    visao = 'VISAOINEXISTENTE'
    response = jwt_authenticated_client_u.get(
        f'/api/usuarios/usuarios-servidores-por-visao/?visao={visao}',
        content_type='application/json'
    )

    result = json.loads(response.content)

    erro = {
        'erro': 'parametro_incorreto',
        'mensagem': f"A visão {visao} não é uma visão válida. Esperado UE, DRE ou SME."
    }

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert result == erro


def test_action_usuarios_servidores_por_visao(
    jwt_authenticated_client_u
):
    response = jwt_authenticated_client_u.get(
        f'/api/usuarios/usuarios-servidores-por-visao/?visao=SME',
        content_type='application/json'
    )

    assert response.status_code == status.HTTP_200_OK
