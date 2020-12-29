import pytest

from django.contrib.auth.models import Permission
from model_bakery import baker

from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType


@pytest.fixture
def permissoes_associacao():
    permissoes = [
        Permission.objects.filter(codename='view_associacao').first(),
        Permission.objects.filter(codename='change_associacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_cobrancas_prestacoes():
    permissoes = [
        Permission.objects.filter(codename='view_cobrancaprestacaoconta').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_observacoes_conciliacao():
    permissoes = [
        Permission.objects.filter(codename='view_observacaoconciliacao').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_prestacoes_conta():
    permissoes = [
        Permission.objects.filter(codename='view_prestacaoconta').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_processo_associacao():
    permissoes = [
        Permission.objects.filter(codename='view_processoassociacao').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_tipo_devolucao():
    permissoes = [
        Permission.objects.filter(codename='view_tipodevolucaoaotesouro').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_unidades():
    permissoes = [
        Permission.objects.filter(codename='view_unidade').first(),
    ]

    return permissoes


@pytest.fixture
def permissoes_dashboard_dre():
    permissoes = [
        Permission.objects.create(
            name="visualizar dados dre",
            codename='view_dashboard_dre',
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def permissoes_associacoes_dre():
    permissoes = [
        Permission.objects.create(
            name="visualizar associacoes dre",
            codename='view_associacao_dre',
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def permissoes_dadosdiretoria_dre():
    permissoes = [
        Permission.objects.create(
            name="visualizar dados diretoria dre",
            codename='view_dadosdiretoria_dre',
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def permissoes_regularidade_dre():
    permissoes = [
        Permission.objects.create(
            name="visualizar regularidade dre",
            codename='view_regularidade_dre',
            content_type=ContentType.objects.filter(app_label="auth").first()
        ),
    ]

    return permissoes


@pytest.fixture
def grupo_associacao(permissoes_associacao):
    g = Grupo.objects.create(name="associacao")
    g.permissions.add(*permissoes_associacao)
    return g


@pytest.fixture
def grupo_cobrancas_prestacoes(permissoes_cobrancas_prestacoes):
    g = Grupo.objects.create(name="cobrancas_prestacoes")
    g.permissions.add(*permissoes_cobrancas_prestacoes)
    return g


@pytest.fixture
def grupo_observacoes_conciliacao(permissoes_observacoes_conciliacao):
    g = Grupo.objects.create(name="observacoes_conciliacao")
    g.permissions.add(*permissoes_observacoes_conciliacao)
    return g


@pytest.fixture
def grupo_prestacoes_conta(permissoes_prestacoes_conta):
    g = Grupo.objects.create(name="prestacoes_conta")
    g.permissions.add(*permissoes_prestacoes_conta)
    return g


@pytest.fixture
def grupo_processo_associacao(permissoes_processo_associacao):
    g = Grupo.objects.create(name="processo_associacao")
    g.permissions.add(*permissoes_processo_associacao)
    return g


@pytest.fixture
def grupo_tipo_devolucao(permissoes_tipo_devolucao):
    g = Grupo.objects.create(name="tipo_devolucao")
    g.permissions.add(*permissoes_tipo_devolucao)
    return g


@pytest.fixture
def grupo_unidades(permissoes_unidades):
    g = Grupo.objects.create(name="unidades")
    g.permissions.add(*permissoes_unidades)
    return g


@pytest.fixture
def grupo_dashboard_dre(permissoes_dashboard_dre):
    g = Grupo.objects.create(name="dashboard_dre")
    g.permissions.add(*permissoes_dashboard_dre)
    return g


@pytest.fixture
def grupo_associacao_dre(permissoes_associacoes_dre):
    g = Grupo.objects.create(name="associacao_dre")
    g.permissions.add(*permissoes_associacoes_dre)
    return g


@pytest.fixture
def grupo_dadosdiretoria_dre(permissoes_dadosdiretoria_dre):
    g = Grupo.objects.create(name="dadosdiretoria_dre")
    g.permissions.add(*permissoes_dadosdiretoria_dre)
    return g


@pytest.fixture
def grupo_regularidade_dre(permissoes_regularidade_dre):
    g = Grupo.objects.create(name="gruporegulariade_dre")
    g.permissions.add(*permissoes_regularidade_dre)
    return g


@pytest.fixture
def usuario_permissao_associacao(
        unidade,
        grupo_associacao,
        grupo_cobrancas_prestacoes,
        grupo_observacoes_conciliacao,
        grupo_prestacoes_conta,
        grupo_processo_associacao,
        grupo_tipo_devolucao,
        grupo_unidades,
        grupo_dashboard_dre,
        grupo_associacao_dre,
        grupo_dadosdiretoria_dre,
        grupo_regularidade_dre):

    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(
        grupo_associacao,
        grupo_cobrancas_prestacoes,
        grupo_observacoes_conciliacao,
        grupo_prestacoes_conta,
        grupo_processo_associacao,
        grupo_tipo_devolucao,
        grupo_unidades,
        grupo_dashboard_dre,
        grupo_associacao_dre,
        grupo_dadosdiretoria_dre,
        grupo_regularidade_dre)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_a(client, usuario_permissao_associacao):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_associacao.username,
                                              'senha': usuario_permissao_associacao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def parametro_fique_de_olho_rel_dre_abc():
    return baker.make(
        'ParametroFiqueDeOlhoRelDre',
        fique_de_olho='abc',
    )
