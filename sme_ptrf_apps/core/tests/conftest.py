import pytest

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def permissoes_associacao():
    permissoes = [
        Permission.objects.filter(codename='add_associacao').first(),
        Permission.objects.filter(codename='view_associacao').first(),
        Permission.objects.filter(codename='change_associacao').first(),
        Permission.objects.filter(codename='delete_associacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_ata():
    permissoes = [
        Permission.objects.filter(codename='add_ata').first(),
        Permission.objects.filter(codename='view_ata').first(),
        Permission.objects.filter(codename='change_ata').first(),
        Permission.objects.filter(codename='delete_ata').first()
    ]

    return permissoes


@pytest.fixture
def grupo_associacao(permissoes_associacao):
    g = Group.objects.create(name="associacao")
    g.permissions.add(*permissoes_associacao)
    return g


@pytest.fixture
def grupo_ata(permissoes_ata):
    g = Group.objects.create(name="ata")
    g.permissions.add(*permissoes_ata)
    return g


@pytest.fixture
def usuario_permissao_associacao(unidade, grupo_associacao, grupo_ata):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_associacao, grupo_ata)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_a(client, usuario_permissao_associacao):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_associacao.username,
                                              'senha': usuario_permissao_associacao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client
