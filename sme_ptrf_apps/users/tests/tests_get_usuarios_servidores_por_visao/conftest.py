import pytest

from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model

from model_bakery import baker

from sme_ptrf_apps.users.models import Grupo


@pytest.fixture
def dre_teste_get_usuarios_servidores_por_visao():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE', nome='DRE teste', sigla='TT')


@pytest.fixture
def unidade_teste_get_usuarios_servidores_por_visao(dre_teste_get_usuarios_servidores_por_visao):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre_teste_get_usuarios_servidores_por_visao,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def visao_ue_teste_get_usuarios_servidores_por_visao():
    return baker.make('Visao', nome='UE')


@pytest.fixture
def visao_sme_teste_get_usuarios_servidores_por_visao():
    return baker.make('Visao', nome='SME')


@pytest.fixture
def permissao1_teste_get_usuarios_servidores_por_visao():
    return Permission.objects.filter(codename='view_tipodevolucaoaotesouro').first()


@pytest.fixture
def grupo_1_teste_get_usuarios_servidores_por_visao(permissao1_teste_get_usuarios_servidores_por_visao, visao_ue_teste_get_usuarios_servidores_por_visao):
    g = Grupo.objects.create(name="grupo1")
    g.permissions.add(permissao1_teste_get_usuarios_servidores_por_visao)
    g.visoes.add(visao_ue_teste_get_usuarios_servidores_por_visao)
    g.descricao = "Descrição grupo 1"
    g.save()
    return g


@pytest.fixture
def usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao(
    unidade_teste_get_usuarios_servidores_por_visao,
    grupo_1_teste_get_usuarios_servidores_por_visao,
    visao_ue_teste_get_usuarios_servidores_por_visao
):
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(
        username=login,
        password=senha,
        email=email,
        e_servidor=True,
        name="Usuario Servidor com Visao UE"
    )
    user.unidades.add(unidade_teste_get_usuarios_servidores_por_visao)
    user.groups.add(grupo_1_teste_get_usuarios_servidores_por_visao)
    user.visoes.add(visao_ue_teste_get_usuarios_servidores_por_visao)
    user.save()
    return user


@pytest.fixture
def usuario__nao_eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao(
    unidade_teste_get_usuarios_servidores_por_visao,
    grupo_1_teste_get_usuarios_servidores_por_visao,
    visao_ue_teste_get_usuarios_servidores_por_visao
):
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(
        username=login,
        password=senha,
        email=email,
        e_servidor=False,
        name="Usuario Não Servidor com Visao UE"
    )
    user.unidades.add(unidade_teste_get_usuarios_servidores_por_visao)
    user.groups.add(grupo_1_teste_get_usuarios_servidores_por_visao)
    user.visoes.add(visao_ue_teste_get_usuarios_servidores_por_visao)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_u(client, usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao):
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
        resp = api_client.post('/api/login', {'login': usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao.username,
                                              'senha': usuario__eh_servidor_para_teste_teste_get_usuarios_servidores_por_visao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client
