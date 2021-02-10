import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.core.choices import RepresentacaoCargo
from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


@pytest.fixture
def unidade_diferente(dre):
    return baker.make(
        'Unidade',
        nome='Escola Unidade Diferente',
        tipo_unidade='EMEI',
        codigo_eol='123459',
        dre=dre,
        sigla='ET2',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='100',
        complemento='fundos',
        telefone='99212627',
        email='emeijopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Amaro Pedro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def visao_ue():
    return baker.make('Visao', nome='UE')


@pytest.fixture
def visao_dre():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def visao_sme():
    return baker.make('Visao', nome='SME')


@pytest.fixture
def permissao1():
    return Permission.objects.filter(codename='view_tipodevolucaoaotesouro').first()


@pytest.fixture
def permissao2():
    return Permission.objects.filter(codename='view_unidade').first()


@pytest.fixture
def grupo_1(permissao1, visao_ue):
    g = Grupo.objects.create(name="grupo1")
    g.permissions.add(permissao1)
    g.visoes.add(visao_ue)
    g.descricao = "Descrição grupo 1"
    g.save()
    return g


@pytest.fixture
def grupo_2(permissao2, visao_dre):
    g = Grupo.objects.create(name="grupo2")
    g.permissions.add(permissao2)
    g.visoes.add(visao_dre)
    g.descricao = "Descrição grupo 2"
    g.save()
    return g


@pytest.fixture
def grupo_3(permissao1, permissao2, visao_dre, visao_sme):
    g = Grupo.objects.create(name="grupo3")
    g.permissions.add(permissao1, permissao2)
    g.visoes.add(visao_dre, visao_sme)
    g.descricao = "Descrição grupo 3"
    g.save()
    return g


@pytest.fixture
def usuario_para_teste(
        unidade,
        grupo_1,
        visao_ue):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_1)
    user.visoes.add(visao_ue)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_u(client, usuario_para_teste):
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
        resp = api_client.post('/api/login', {'login': usuario_para_teste.username,
                                              'senha': usuario_para_teste.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def usuario_2(
        unidade_diferente,
        grupo_2,
        grupo_3,
        visao_dre,
        visao_sme):

    senha = 'Sgp1981'
    login = '7211981'
    email = 'sme1981@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_diferente)
    user.groups.add(grupo_2, grupo_3)
    user.visoes.add(visao_dre, visao_sme)
    user.save()
    return user


@pytest.fixture
def usuario_3(
        unidade,
        grupo_2,
        visao_dre,
        visao_ue):

    senha = 'Sgp8198'
    login = '7218198'
    email = 'sme8198@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, name="Arthur Marques")
    user.unidades.add(unidade)
    user.groups.add(grupo_2)
    user.visoes.add(visao_dre, visao_ue)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_u2(client, usuario_2):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": usuario_2.username
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_2.username,
                                              'senha': usuario_2.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_consulta_grupos(
        jwt_authenticated_client_u2,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2,
        grupo_3):

    response = jwt_authenticated_client_u2.get("/api/usuarios/grupos/?visao=DRE", content_type='application/json')
    result = response.json()
    esperado = [
        {
            "id": str(grupo_2.id),
            "nome": grupo_2.name,
            "descricao": grupo_2.descricao
        },
        {
            "id": str(grupo_3.id),
            "nome": grupo_3.name,
            "descricao": grupo_3.descricao
        }]

    assert result == esperado


def test_lista_usuarios(
        jwt_authenticated_client_u,
        usuario_para_teste,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u.get("/api/usuarios/?visao=DRE", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'username': usuario_3.username,
            'email': usuario_3.email,
            'name': usuario_3.name,
            'url': f'http://testserver/api/esqueci-minha-senha/{usuario_3.username}/',
            'tipo_usuario': usuario_3.tipo_usuario,
            'groups': [{'id': grupo_2.id, 'name': grupo_2.name, 'descricao': grupo_2.descricao}]
        }
    ]
    assert result == esperado


def test_filtro_por_grupo_lista_usuarios(
        jwt_authenticated_client_u2,
        usuario_2,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u2.get(
        f"/api/usuarios/?visao=DRE&groups__id={grupo_2.id}", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'username': '7218198',
            'email': 'sme8198@amcom.com.br',
            'name': 'Arthur Marques',
            'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
            'tipo_usuario': usuario_3.tipo_usuario,
            'groups': [
                {
                   'id': grupo_2.id,
                   'name': 'grupo2',
                   'descricao': 'Descrição grupo 2'
                }
            ]
        }
    ]
    assert result == esperado


def test_filtro_por_nome_lista_usuarios(
        jwt_authenticated_client_u2,
        usuario_2,
        usuario_3,
        visao_ue,
        visao_dre,
        visao_sme,
        permissao1,
        permissao2,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u2.get(f"/api/usuarios/?visao=DRE&search=Arth", content_type='application/json')
    result = response.json()
    esperado = [
        {'id': usuario_3.id,
         'username': '7218198',
         'email': 'sme8198@amcom.com.br',
         'name': 'Arthur Marques',
         'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
         'tipo_usuario': usuario_3.tipo_usuario,
         'groups': [
             {
                'id': grupo_2.id,
                'name': 'grupo2',
                'descricao': 'Descrição grupo 2'}]
         }
    ]
    assert result == esperado


def test_criar_usuario_servidor(
        jwt_authenticated_client_u,
        grupo_1,
        grupo_2,
        visao_dre):

    payload = {
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'username': "9876543",
        'name': "Lukaku Silva",
        'email': 'lukaku@gmail.com',
        'visao': "DRE",
        'groups': [
            grupo_1.id,
            grupo_2.id
        ]
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': '9876543',
        'email': 'lukaku@gmail.com',
        'name': 'Lukaku Silva',
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'groups': [grupo_1.id, grupo_2.id]
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert len(u.visoes.all()) > 0
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_criar_usuario_servidor_sem_email_e_sem_nome(
        jwt_authenticated_client_u,
        grupo_1,
        grupo_2,
        visao_dre):

    payload = {
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'username': "9876543",
        'name': "",
        'email': "",
        'visao': "DRE",
        'groups': [
            grupo_1.id,
            grupo_2.id
        ]
    }
    response = jwt_authenticated_client_u.post(
        "/api/usuarios/", data=json.dumps(payload), content_type='application/json')
    result = response.json()
    esperado = {
        'username': '9876543',
        'email': '',
        'name': '',
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'groups': [grupo_1.id, grupo_2.id]
    }
    User = get_user_model()
    u = User.objects.filter(username='9876543').first()

    assert len(u.visoes.all()) > 0
    assert response.status_code == status.HTTP_201_CREATED
    assert result == esperado


def test_atualizar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3,
        usuario_2,
        visao_ue,
        visao_dre,
        visao_sme,
        grupo_1,
        grupo_2):

    assert not usuario_2.visoes.filter(nome='UE').first()

    payload = {
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'username': usuario_2.username,
        'name': usuario_2.name,
        'email': 'novoEmail@gmail.com',
        'visao': "UE",
        'groups': [
            grupo_1.id
        ]
    }

    response = jwt_authenticated_client_u.put(
        f"/api/usuarios/{usuario_2.id}/", data=json.dumps(payload), content_type='application/json')
    result = response.json()

    esperado = {
        'username': usuario_2.username,
        'email': 'novoEmail@gmail.com',
        'name': usuario_2.name,
        'tipo_usuario': RepresentacaoCargo.SERVIDOR.name,
        'groups': [grupo_1.id]
    }

    assert usuario_2.visoes.filter(nome='UE').first()
    assert result == esperado


def test_deletar_usuario_servidor(
        jwt_authenticated_client_u,
        usuario_3
):

    from django.contrib.auth import get_user_model

    User = get_user_model()
    assert User.objects.filter(id=usuario_3.id).exists()

    response = jwt_authenticated_client_u.delete(
        f"/api/usuarios/{usuario_3.id}/", content_type='application/json')
    assert not User.objects.filter(id=usuario_3.id).exists()


def test_consulta_informacao_usuario(jwt_authenticated_client_u):
    path = 'sme_ptrf_apps.users.api.views.user.SmeIntegracaoService.informacao_usuario_sgp'
    with patch(path) as mock_get:
        data = {
            'cpf': '12808888813',
            'nome': 'LUCIMARA CARDOSO RODRIGUES',
            'codigoRf': '7210418',
            'email': 'tutu@gmail.com',
            'emailValido': True
        }

        mock_get.return_value = data

        username = '7210418'
        response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username={7210418}')
        result = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK
        assert result == data


def test_consulta_informacao_usuario_sem_username(jwt_authenticated_client_u):
    response = jwt_authenticated_client_u.get(f'/api/usuarios/consultar/?username=')
    result = json.loads(response.content)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert result == "Parâmetro username obrigatório."


def test_lista_usuarios_por_unidade(
        jwt_authenticated_client_u,
        usuario_para_teste,
        usuario_2,
        usuario_3,
        associacao,
        grupo_1,
        grupo_2):

    response = jwt_authenticated_client_u.get(f"/api/usuarios/?associacao_uuid={associacao.uuid}", content_type='application/json')
    result = response.json()
    esperado = [
        {
            'id': usuario_3.id,
            'name': 'Arthur Marques',
            'tipo_usuario': 'Servidor',
            'url': 'http://testserver/api/esqueci-minha-senha/7218198/',
            'username': '7218198',
            'email': 'sme8198@amcom.com.br',
            'groups': [
                {
                    'descricao': 'Descrição grupo 2',
                    'id': grupo_2.id,
                    'name': 'grupo2'
                }],
        },
        {
            'id': usuario_para_teste.id,
            'name': 'LUCIA HELENA',
            'tipo_usuario': 'Servidor',
            'url': 'http://testserver/api/esqueci-minha-senha/7210418/',
            'username': '7210418',
            'email': 'luh@gmail.com',
            'groups': [
                {
                    'descricao': 'Descrição grupo 1',
                    'id': grupo_1.id,
                    'name': 'grupo1'
                }],
        }

    ]
    print(result)
    assert result == esperado
