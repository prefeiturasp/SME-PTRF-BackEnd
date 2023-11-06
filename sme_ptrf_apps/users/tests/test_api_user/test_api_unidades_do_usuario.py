import json

import pytest

from rest_framework import status
from waffle.testutils import override_flag

pytestmark = pytest.mark.django_db


def test_endpoint_unidades_do_usuario(jwt_authenticated_client_u, usuario_nao_servidor):
    username = usuario_nao_servidor.username
    
    with override_flag('gestao-usuarios', active=True):
        response = jwt_authenticated_client_u.get(
            f'/api/usuarios-v2/unidades-do-usuario/?username={username}&visao_base=SME&uuid_unidade=SME')
        assert response.status_code == status.HTTP_200_OK
        
    with override_flag('gestao-usuarios', active=False):
        response = jwt_authenticated_client_u.get(
            f'/api/usuarios-v2/unidades-do-usuario/?username={username}&visao_base=SME&uuid_unidade=SME')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    


def test_endpoint_habilitar_acesso(jwt_authenticated_client_u, usuario_nao_servidor, unidade):
    payload = {
        "username": f"{usuario_nao_servidor.username}",
        "uuid_unidade": f"{unidade.uuid}",
    }

    with override_flag('gestao-usuarios', active=True):
        response = jwt_authenticated_client_u.patch(
            f'/api/usuarios-v2/habilitar-acesso/', data=json.dumps(payload), content_type='application/json')

        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result['mensagem'] == "Acesso ativado para unidade selecionada"
        
    with override_flag('gestao-usuarios', active=False):
        response = jwt_authenticated_client_u.patch(
            f'/api/usuarios-v2/habilitar-acesso/', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == status.HTTP_404_NOT_FOUND


def test_endpoint_desabilitar_acesso(jwt_authenticated_client_u, usuario_nao_servidor, unidade):
    payload = {
        "username": f"{usuario_nao_servidor.username}",
        "uuid_unidade": f"{unidade.uuid}",
    }

    with override_flag('gestao-usuarios', active=True):
        response = jwt_authenticated_client_u.patch(
            f'/api/usuarios-v2/desabilitar-acesso/', data=json.dumps(payload), content_type='application/json')

        result = json.loads(response.content)

        assert response.status_code == status.HTTP_200_OK
        assert result['mensagem'] == "Acesso desativado para unidade selecionada"
        
    with override_flag('gestao-usuarios', active=False):
        response = jwt_authenticated_client_u.patch(
            f'/api/usuarios-v2/desabilitar-acesso/', data=json.dumps(payload), content_type='application/json')   
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
