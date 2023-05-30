import json

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.users.models import Grupo

from ....core.choices import MembroEnum, RepresentacaoCargo

pytestmark = pytest.mark.django_db


@pytest.fixture
def presidente_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567432',
        email='arthur@gmail.com'
    )


@pytest.fixture
def presidente_conselho_fiscal(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='José Firmino',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_CONSELHO_FISCAL.name,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567433',
        email='jose@gmail.com'
    )


@pytest.fixture
def censo(unidade):
    return baker.make(
        'Censo',
        unidade=unidade,
        quantidade_alunos=1000,
        ano='2020'
    )


def test_api_retrieve_associacao(jwt_authenticated_client_a, associacao, presidente_associacao,
                                 presidente_conselho_fiscal, censo):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.atualiza_dados_unidade') as mock_patch:
        response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/',
                                                  content_type='application/json')
        result = json.loads(response.content)

        mock_patch.return_value = None

        assert response.status_code == status.HTTP_200_OK
        assert result['uuid'] == str(associacao.uuid)



@pytest.fixture
def permissoes_ver_dados_unidade_dre():
    permissoes = [
        Permission.objects.create(
            name="Ver Dados Unidade",
            codename='view_dados_unidade_dre',
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def grupo_permissoes_unidades_dre(permissoes_ver_dados_unidade_dre):
    g = Grupo.objects.create(name="VerDadosUnidade")
    g.permissions.add(*permissoes_ver_dados_unidade_dre)
    return g


@pytest.fixture
def usuario_permissao_unidades_dre(unidade, grupo_permissoes_unidades_dre):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_permissoes_unidades_dre)
    user.save()
    return user


@pytest.fixture
def usuario_sem_permissao_unidades_dre(unidade):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0419'
    login = '7210419'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_com_permissao(client, usuario_permissao_unidades_dre):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_unidades_dre.username,
                                              'senha': usuario_permissao_unidades_dre.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def jwt_authenticated_client_sem_permissao(client, usuario_sem_permissao_unidades_dre):
    from unittest.mock import patch

    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210419"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_sem_permissao_unidades_dre.username,
                                              'senha': usuario_sem_permissao_unidades_dre.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


def test_api_retrieve_associacao_pode_editar_dados_associacao_nao_encerrada(
    jwt_authenticated_client_a,
    associacao,
    prestacao_conta
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'data_de_encerramento': {
            'data': None,
            'help_text': 'A associação deixará de ser exibida nos períodos posteriores à '
                         'data de encerramento informada.',
            'pode_editar_dados_associacao_encerrada': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result["data_de_encerramento"] == resultado_esperado["data_de_encerramento"]


def test_api_retrieve_associacao_pode_editar_dados_associacao_encerrada(
    jwt_authenticated_client_a,
    associacao_encerrada_2020_1,
    prestacao_conta_2020_1_aprovada_associacao_encerrada
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao_encerrada_2020_1.uuid}/',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'data_de_encerramento': {
            'data': '2020-06-30',
            'help_text': 'A associação deixará de ser exibida nos períodos posteriores à '
                         'data de encerramento informada.',
            'pode_editar_dados_associacao_encerrada': True
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result["data_de_encerramento"] == resultado_esperado["data_de_encerramento"]


def test_api_retrieve_associacao_nao_pode_editar_dados_associacao_encerrada_com_pc_publicada(
    jwt_authenticated_client_a,
    associacao_encerrada_2020_1,
    prestacao_conta_2020_1_aprovada_associacao_encerrada_publicada_diario_oficial
):

    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao_encerrada_2020_1.uuid}/',
                                              content_type='application/json')
    result = json.loads(response.content)

    resultado_esperado = {
        'data_de_encerramento': {
            'data': '2020-06-30',
            'help_text': 'A associação deixará de ser exibida nos períodos posteriores à '
                         'data de encerramento informada.',
            'pode_editar_dados_associacao_encerrada': False
        }
    }

    assert response.status_code == status.HTTP_200_OK
    assert result["data_de_encerramento"] == resultado_esperado["data_de_encerramento"]
