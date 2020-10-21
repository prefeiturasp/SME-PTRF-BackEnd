"""
Testes validando os casos onde o usuário não tem as permissões necessárias para acessar
determinadas rotas.
"""

import json
from datetime import timedelta

import pytest
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.receitas.models import Receita, Repasse

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissoes_receitas():
    content_type = ContentType.objects.filter(model='receita').first()
    permissoes = [
        Permission.objects.filter(codename='add_receita').first(),
        Permission.objects.filter(codename='view_receita').first(),
        Permission.objects.filter(codename='change_receita').first(),
        Permission.objects.filter(codename='delete_receita').first()
    ]

    return permissoes


@pytest.fixture
def grupo_receita(permissoes_receitas):
    g = Group.objects.create(name="receita")
    for p in permissoes_receitas:
        g.permissions.add(p)
    return g


@pytest.fixture
def usuario(unidade, grupo_receita):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_receita)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_p(client, usuario):
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
        resp = api_client.post('/api/login', {'login': usuario.username, 'senha': usuario.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_permission_create_receita(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita
):
    response = jwt_authenticated_client_p.post(
        '/api/receitas/', data=json.dumps(payload_receita), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


@pytest.fixture
def grupo_sem_permissao_criar_receita():
    content_type = ContentType.objects.filter(model='receita').first()
    g = Group.objects.create(name="receita")
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


def test_without_permission_to_create_receita(
    jwt_authenticated_client_sem_permissao,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita
):
    response = jwt_authenticated_client_sem_permissao.post(
        '/api/receitas/', data=json.dumps(payload_receita), content_type='application/json')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_retrive_receitas_sem_permissao(
        jwt_authenticated_client_sem_permissao,
        tipo_receita,
        detalhe_tipo_receita,
        receita,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao):
    response = jwt_authenticated_client_sem_permissao.get(
        f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def repasse_teste(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=0,
        valor_capital=0,
        valor_livre=1000.28,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


@pytest.fixture
def receita_teste(associacao, conta_associacao, acao_associacao, tipo_receita, periodo, repasse_teste):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        repasse=repasse_teste
    )


def test_update_receita_repasse_livre_aplicacao_com_valores_capital_e_custeio_sem_permissao(
    jwt_authenticated_client_sem_permissao,
    tipo_receita_repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_teste,
    receita_teste
):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'LIVRE',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id
    }
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse_teste.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_sem_permissao.put(
            f'/api/receitas/{receita_teste.uuid}/?associacao_uuid={associacao.uuid}',
            data=json.dumps(payload),
            content_type='application/json')

        assert response.status_code == status.HTTP_403_FORBIDDEN


def test_deleta_receita(
        jwt_authenticated_client_sem_permissao,
        tipo_receita,
        acao,
        acao_associacao,
        associacao,
        tipo_conta,
        conta_associacao,
        receita,
        payload_receita):
    assert Receita.objects.filter(uuid=receita.uuid).exists()

    response = jwt_authenticated_client_sem_permissao.delete(
        f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_403_FORBIDDEN
