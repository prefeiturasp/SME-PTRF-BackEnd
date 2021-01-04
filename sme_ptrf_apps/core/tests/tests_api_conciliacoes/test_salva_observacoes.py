import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

from ...models import ObservacaoConciliacao

pytestmark = pytest.mark.django_db

@pytest.fixture
def permissoes_salvar_conciliacao_bancaria():
    permissoes = [
        Permission.objects.create(
            name="Editar conciliação bancária", 
            codename='change_conciliacao_bancaria', 
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def grupo_salvar_conciliacao_bancaria(permissoes_salvar_conciliacao_bancaria):
    g = Grupo.objects.create(name="grupo_salvar_conciliacao_bancaria")
    g.permissions.add(*permissoes_salvar_conciliacao_bancaria)
    return g


@pytest.fixture
def usuario_permissao_salvar_conciliacao_bancaria(
        unidade,
        grupo_salvar_conciliacao_bancaria):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210411'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    #user.groups.add(grupo_salvar_conciliacao_bancaria)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_salvar_obervacao(client, usuario_permissao_salvar_conciliacao_bancaria):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210411"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao_salvar_conciliacao_bancaria.username,
                                              'senha': usuario_permissao_salvar_conciliacao_bancaria.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_api_salva_observacoes_conciliacao(jwt_authenticated_client_salvar_obervacao, periodo, conta_associacao_cartao, acao_associacao_ptrf):
    url = f'/api/conciliacoes/salvar-observacoes/'

    observacao = "Teste observações."
    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacoes": [{
            "acao_associacao_uuid": f'{acao_associacao_ptrf.uuid}',
            "observacao": observacao
        }]
    }

    response = jwt_authenticated_client_salvar_obervacao.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert ObservacaoConciliacao.objects.exists()


def test_api_salva_observacoes_conciliacao_vazia(jwt_authenticated_client_salvar_obervacao, periodo, conta_associacao_cartao, acao_associacao_ptrf):
    url = f'/api/conciliacoes/salvar-observacoes/'

    observacao = ""
    payload = {
        "periodo_uuid": f'{periodo.uuid}',
        "conta_associacao_uuid": f'{conta_associacao_cartao.uuid}',
        "observacoes": [{
            "acao_associacao_uuid": f'{acao_associacao_ptrf.uuid}',
            "observacao": observacao
        }]
    }

    response = jwt_authenticated_client_salvar_obervacao.patch(url, data=json.dumps(payload), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert not ObservacaoConciliacao.objects.exists()
