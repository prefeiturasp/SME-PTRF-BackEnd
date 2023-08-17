import json

import pytest
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

pytestmark = pytest.mark.django_db


def test_repasses_pendentes(
        jwt_authenticated_client_p,
        periodo,
        repasse,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_p.get(
        f'/api/repasses/pendentes/?associacao={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{repasse.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert result_uuids == uuids_esperado


def test_repasses_pendentes_livre_aplicacao(
        jwt_authenticated_client_p,
        periodo_2020_1,
        repasse_2020_1_livre_aplicacao_pendente,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_p.get(
        f'/api/repasses/pendentes/?associacao={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{repasse_2020_1_livre_aplicacao_pendente.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert result_uuids == uuids_esperado

@pytest.fixture
def grupo_sem_permissao_criar_receita():
    content_type = ContentType.objects.filter(model='receita').first()
    g = Grupo.objects.create(name="receita")
    g.permissions.add(
        Permission.objects.create(codename='algo_receita', name='Can Algo', content_type=content_type)
    )
    return g


@pytest.fixture
def usuario_sem_permissao(unidade, grupo_sem_permissao_criar_receita):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sem_permissao_criar_receita)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sem_permissao(client, usuario_sem_permissao):
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
        resp = api_client.post('/api/login', {'login': usuario_sem_permissao.username,
                                              'senha': usuario_sem_permissao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_repasses_pendentes_sem_permissao(
        jwt_authenticated_client_sem_permissao,
        periodo,
        repasse,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):

    response = jwt_authenticated_client_sem_permissao.get(
        f'/api/repasses/pendentes/?acao-associacao={acao_associacao.uuid}&data=02/09/2019', content_type='application/json')

    assert response.status_code == HTTP_403_FORBIDDEN
