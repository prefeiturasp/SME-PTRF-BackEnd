import pytest

from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from model_bakery import baker

from sme_ptrf_apps.users.models import Grupo


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
def unidade_ue_271170(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste 271170',
        tipo_unidade='EMEI',
        codigo_eol='271170',
        dre=dre,
        sigla='ET9',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='100',
        complemento='fundos',
        telefone='99212627',
        email='teste271170@sme.prefeitura.sp.gov.br',
        diretor_nome='Maria Testando',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def associacao_271170(unidade_ue_271170):
    return baker.make(
        'Associacao',
        nome='Associacao 271170',
        cnpj='62.738.735/0001-74',
        unidade=unidade_ue_271170,
        status_regularidade='PENDENTE'
    )


@pytest.fixture
def membro_associacao_00746198701(associacao_271170):
    return baker.make(
        'MembroAssociacao',
        nome='Jose Testando',
        associacao=associacao_271170,
        cargo_associacao="VOGAL_1",
        cargo_educacao='',
        representacao="ESTUDANTE",
        codigo_identificacao='',
        email='jose@teste.com',
        cpf='007.461.987-01',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila Teste',
        endereco='Rua Teste, 57'
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
    nome  = 'Usuario 2'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, name=nome)
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
    user = User.objects.create_user(username=login, password=senha, email=email, name="Arthur Marques", e_servidor=True)
    user.unidades.add(unidade)
    user.groups.add(grupo_2)
    user.visoes.add(visao_dre, visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_duas_unidades(
        unidade,
        unidade_diferente,
        grupo_2,
        visao_dre,
        visao_ue):

    senha = 'Sgp8198'
    login = '7218198'
    email = 'sme8198@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, name="Arthur Marques", e_servidor=True)
    user.unidades.add(unidade)
    user.unidades.add(unidade_diferente)
    user.groups.add(grupo_2)
    user.visoes.add(visao_dre, visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_servidor(
        unidade,
        grupo_2,
        visao_dre,
        visao_ue):

    senha = 'Sgp8198'
    login = '7218198'
    email = 'sme8198@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, name="Arthur Marques", e_servidor=True)
    user.unidades.add(unidade)
    user.groups.add(grupo_2)
    user.visoes.add(visao_dre, visao_ue)
    user.save()
    return user


@pytest.fixture
def usuario_nao_servidor(
        unidade,
        grupo_2,
        visao_dre,
        visao_ue):

    senha = 'Sgp8701'
    login = '00746198701'
    email = 'teste123@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, name="Arthur Marques", e_servidor=False)
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
