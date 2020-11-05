import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissoes_exportar():
    permissoes = [
        Permission.objects.create(
            name="Exportar Dados Diretoria", 
            codename='export_dados_associacao', 
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def grupo_exportar(permissoes_exportar):
    g = Grupo.objects.create(name="Exportar")
    g.permissions.add(*permissoes_exportar)
    return g


@pytest.fixture
def usuario_permissao_exportar(unidade, grupo_exportar):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_exportar)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_export(client, usuario_permissao_exportar):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_exportar.username,
                                              'senha': usuario_permissao_exportar.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_exportar(jwt_authenticated_client_export, associacao):
    url = f"/api/associacoes/{associacao.uuid}/exportar/"
    response = jwt_authenticated_client_export.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Disposition'][0] == 'attachment; filename=associacao.xlsx'
    assert [t[1] for t in list(response.items()) if t[0] ==
            'Content-Type'][0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
