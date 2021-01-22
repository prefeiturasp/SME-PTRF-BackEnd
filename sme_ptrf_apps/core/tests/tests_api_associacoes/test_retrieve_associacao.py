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


def test_api_retrieve_associacao(jwt_authenticated_client_a, associacao, presidente_associacao, presidente_conselho_fiscal, censo):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.atualiza_dados_unidade') as mock_patch:
        response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/', content_type='application/json')
        result = json.loads(response.content)

        mock_patch.return_value = None

        result_esperado = {
            'uuid': f'{associacao.uuid}',
            'id': associacao.id,
            'ccm': f'{associacao.ccm}',
            'cnpj': f'{associacao.cnpj}',
            'email': f'{associacao.email}',
            'nome': f'{associacao.nome}',
            'status_regularidade': f'{associacao.status_regularidade}',
            'motivo_nao_regularidade': '',
            'presidente_associacao': {
                'nome': presidente_associacao.nome,
                'email': presidente_associacao.email,
                'cargo_educacao': presidente_associacao.cargo_educacao
            },
            'presidente_conselho_fiscal': {
                'nome': presidente_conselho_fiscal.nome,
                'email': presidente_conselho_fiscal.email,
                'cargo_educacao': presidente_conselho_fiscal.cargo_educacao
            },
            'processo_regularidade': '123456',
            'periodo_inicial': {
                'data_fim_realizacao_despesas': '2019-08-31',
                'data_inicio_realizacao_despesas': '2019-01-01',
                'referencia': '2019.1',
                'referencia_por_extenso': '1° repasse de 2019',
                'uuid': f'{associacao.periodo_inicial.uuid}'
            },
            'unidade': {
                'codigo_eol': f'{associacao.unidade.codigo_eol}',
                'dre': {
                    'codigo_eol': f'{associacao.unidade.dre.codigo_eol}',
                    'nome': f'{associacao.unidade.dre.nome}',
                    'sigla': f'{associacao.unidade.dre.sigla}',
                    'tipo_unidade': 'DRE',
                    'uuid': f'{associacao.unidade.dre.uuid}'
                },
                'dre_cnpj': f'{associacao.unidade.dre_cnpj}',
                'dre_designacao_ano': f'{associacao.unidade.dre_designacao_ano}',
                'dre_designacao_portaria': f'{associacao.unidade.dre_designacao_portaria}',
                'dre_diretor_regional_nome': f'{associacao.unidade.dre_diretor_regional_nome}',
                'dre_diretor_regional_rf': f'{associacao.unidade.dre_diretor_regional_rf}',
                'nome': f'{associacao.unidade.nome}',
                'sigla': f'{associacao.unidade.sigla}',
                'tipo_unidade': f'{associacao.unidade.tipo_unidade}',
                'uuid': f'{associacao.unidade.uuid}',
                'email': f'{associacao.unidade.email}',
                'qtd_alunos': associacao.unidade.qtd_alunos,
                'tipo_logradouro': f'{associacao.unidade.tipo_logradouro}',
                'logradouro': f'{associacao.unidade.logradouro}',
                'numero': f'{associacao.unidade.numero}',
                'complemento': f'{associacao.unidade.complemento}',
                'bairro': f'{associacao.unidade.bairro}',
                'cep': f'{associacao.unidade.cep}',
                'telefone': f'{associacao.unidade.telefone}',
                'diretor_nome': f'{associacao.unidade.diretor_nome}',
            },
        }

        assert response.status_code == status.HTTP_200_OK
        assert result == result_esperado


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


def test_api_retrieve_associacao_apenas_com_permissao_ver_dados_unidade_dre(jwt_authenticated_client_com_permissao, associacao, presidente_associacao, presidente_conselho_fiscal, censo):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.atualiza_dados_unidade') as mock_patch:
        response = jwt_authenticated_client_com_permissao.get(f'/api/associacoes/{associacao.uuid}/', content_type='application/json')
        result = json.loads(response.content)

        mock_patch.return_value = None

        result_esperado = {
            'uuid': f'{associacao.uuid}',
            'id': associacao.id,
            'ccm': f'{associacao.ccm}',
            'cnpj': f'{associacao.cnpj}',
            'email': f'{associacao.email}',
            'nome': f'{associacao.nome}',
            'status_regularidade': f'{associacao.status_regularidade}',
            'motivo_nao_regularidade': '',
            'presidente_associacao': {
                'nome': presidente_associacao.nome,
                'email': presidente_associacao.email,
                'cargo_educacao': presidente_associacao.cargo_educacao
            },
            'presidente_conselho_fiscal': {
                'nome': presidente_conselho_fiscal.nome,
                'email': presidente_conselho_fiscal.email,
                'cargo_educacao': presidente_conselho_fiscal.cargo_educacao
            },
            'processo_regularidade': '123456',
            'periodo_inicial': {
                'data_fim_realizacao_despesas': '2019-08-31',
                'data_inicio_realizacao_despesas': '2019-01-01',
                'referencia': '2019.1',
                'referencia_por_extenso': '1° repasse de 2019',
                'uuid': f'{associacao.periodo_inicial.uuid}'
            },
            'unidade': {
                'codigo_eol': f'{associacao.unidade.codigo_eol}',
                'dre': {
                    'codigo_eol': f'{associacao.unidade.dre.codigo_eol}',
                    'nome': f'{associacao.unidade.dre.nome}',
                    'sigla': f'{associacao.unidade.dre.sigla}',
                    'tipo_unidade': 'DRE',
                    'uuid': f'{associacao.unidade.dre.uuid}'
                },
                'dre_cnpj': f'{associacao.unidade.dre_cnpj}',
                'dre_designacao_ano': f'{associacao.unidade.dre_designacao_ano}',
                'dre_designacao_portaria': f'{associacao.unidade.dre_designacao_portaria}',
                'dre_diretor_regional_nome': f'{associacao.unidade.dre_diretor_regional_nome}',
                'dre_diretor_regional_rf': f'{associacao.unidade.dre_diretor_regional_rf}',
                'nome': f'{associacao.unidade.nome}',
                'sigla': f'{associacao.unidade.sigla}',
                'tipo_unidade': f'{associacao.unidade.tipo_unidade}',
                'uuid': f'{associacao.unidade.uuid}',
                'email': f'{associacao.unidade.email}',
                'qtd_alunos': associacao.unidade.qtd_alunos,
                'tipo_logradouro': f'{associacao.unidade.tipo_logradouro}',
                'logradouro': f'{associacao.unidade.logradouro}',
                'numero': f'{associacao.unidade.numero}',
                'complemento': f'{associacao.unidade.complemento}',
                'bairro': f'{associacao.unidade.bairro}',
                'cep': f'{associacao.unidade.cep}',
                'telefone': f'{associacao.unidade.telefone}',
                'diretor_nome': f'{associacao.unidade.diretor_nome}',
            },
        }

        assert response.status_code == status.HTTP_200_OK
        assert result == result_esperado


def test_api_retrieve_associacao_apenas_sem_permissao_ver_dados_unidade_dre(jwt_authenticated_client_sem_permissao, associacao, presidente_associacao, presidente_conselho_fiscal, censo):
    from unittest.mock import patch
    with patch('sme_ptrf_apps.core.api.views.associacoes_viewset.atualiza_dados_unidade') as mock_patch:
        response = jwt_authenticated_client_sem_permissao.get(f'/api/associacoes/{associacao.uuid}/', content_type='application/json')
        result = json.loads(response.content)

        mock_patch.return_value = None

        assert response.status_code == status.HTTP_403_FORBIDDEN

