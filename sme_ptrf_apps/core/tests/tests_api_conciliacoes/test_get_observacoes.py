import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissoes_visualizar_conciliacao_bancaria():
    permissoes = [
        Permission.objects.create(
            name="visualizar conciliação bancária", 
            codename='view_conciliacao_bancaria', 
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def grupo_ver_conciliacao_bancaria(permissoes_visualizar_conciliacao_bancaria):
    g = Grupo.objects.create(name="grupo_visualizar_conciliacao_bancaria")
    g.permissions.add(*permissoes_visualizar_conciliacao_bancaria)
    return g


@pytest.fixture
def usuario_permissao_ver_conciliacao_bancaria(
        unidade,
        grupo_ver_conciliacao_bancaria):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_ver_conciliacao_bancaria)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_obervacao(client, usuario_permissao_ver_conciliacao_bancaria):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_ver_conciliacao_bancaria.username,
                                              'senha': usuario_permissao_ver_conciliacao_bancaria.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_api_get_observacoes_lista_vazia(jwt_authenticated_client_obervacao,
                                         periodo_2020_1,
                                         conta_associacao_cartao
                                         ):
    conta_uuid = conta_associacao_cartao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo_2020_1.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_obervacao.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == []


def test_api_get_observacoes(jwt_authenticated_client_obervacao,
                             periodo,
                             conta_associacao,
                             observacao_conciliacao
                             ):
    conta_uuid = conta_associacao.uuid

    url = f'/api/conciliacoes/observacoes/?periodo={periodo.uuid}&conta_associacao={conta_uuid}'

    response = jwt_authenticated_client_obervacao.get(url, content_type='application/json')

    result = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert result == [
        {
            'acao_associacao_uuid': f'{observacao_conciliacao.acao_associacao.uuid}',
            'observacao': 'Uma bela observação.'
        }
    ]
