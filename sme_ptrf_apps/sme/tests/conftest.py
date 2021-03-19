import pytest
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo


@pytest.fixture
def permissoes_sme():
    permissoes = [
        Permission.objects.filter(codename='sme_leitura').first(),
        Permission.objects.filter(codename='sme_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_sme(permissoes_sme):
    g = Grupo.objects.create(name="sme")
    g.permissions.add(*permissoes_sme)
    return g


@pytest.fixture
def usuario_permissao_sme(unidade, grupo_sme):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '1235678'
    email = 'usuario.sme@gmail.com'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sme)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sme(client, usuario_permissao_sme):
    from unittest.mock import patch
    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "Usuario SME",
            "cpf": "12345678910",
            "email": "usuario.sme@gmail.com",
            "login": "1235678"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_sme.username, 'senha': usuario_permissao_sme.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client
