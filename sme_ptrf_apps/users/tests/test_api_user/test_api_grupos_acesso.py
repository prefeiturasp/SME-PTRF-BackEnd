import json

import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


def test_grupos_disponiveis_por_acesso_e_visao_do_usuario(jwt_authenticated_client_u, usuario_nao_servidor):
    username = usuario_nao_servidor.username

    response = jwt_authenticated_client_u.get(
        f'/api/grupos/grupos-disponiveis-por-acesso-visao/?username={username}&visao_base=SME&uuid_unidade=SME')
    assert response.status_code == status.HTTP_200_OK
    
def test_habilitar_grupo_acesso(jwt_authenticated_client_u, usuario_nao_servidor):
    payload = {
        "username": f"{usuario_nao_servidor.username}",
        "id_grupo": usuario_nao_servidor.groups.first().id
    }
    
    response = jwt_authenticated_client_u.patch(
            f'/api/grupos/habilitar-grupo-acesso/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['mensagem'] == "Grupo de acesso habilitado para o usuario."
        
def test_desabilitar_grupo_acesso(jwt_authenticated_client_u, usuario_nao_servidor):
    payload = {
        "username": f"{usuario_nao_servidor.username}",
        "id_grupo": usuario_nao_servidor.groups.first().id
    }
    
    response = jwt_authenticated_client_u.patch(
            f'/api/grupos/desabilitar-grupo-acesso/', data=json.dumps(payload), content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result['mensagem'] == "Grupo de acesso desabiltiado para o usuario."