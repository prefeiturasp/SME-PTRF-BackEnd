from datetime import date
import pytest
from model_bakery import baker
from ...models import ConsolidadoDRE
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo

pytestmark = pytest.mark.django_db


@pytest.fixture
def permissoes_sme():
    permissoes = [
        Permission.objects.filter(codename='sme_leitura').first(),
        Permission.objects.filter(codename='sme_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_sme(permissoes_sme):
    g = Grupo.objects.create(name="sme")
    g.permissions.add(*permissoes_sme)
    return g


@pytest.fixture
def usuario_permissao_sme(unidade, grupo_sme):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '1235678'
    email = 'usuario.sme@gmail.com'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sme)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sme_teste_comentarios_de_analise_consolidado_dre(client, usuario_permissao_sme):
    from unittest.mock import patch
    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "Usuario SME",
            "cpf": "12345678910",
            "email": "usuario.sme@gmail.com",
            "login": "1235678"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login',
                               {'login': usuario_permissao_sme.username, 'senha': usuario_permissao_sme.password},
                               format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def dre_teste_api_comentario_analise_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A'
    )


@pytest.fixture
def periodo_anterior_teste_api_comentario_analise_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_api_comentario_analise_consolidado_dre(periodo_anterior_teste_api_comentario_analise_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_api_comentario_analise_consolidado_dre,
    )


@pytest.fixture
def consolidado_dre_teste_api_comentario_analise_consolidado_dre(periodo_teste_api_comentario_analise_consolidado_dre,
                                                                 dre_teste_api_comentario_analise_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_api_comentario_analise_consolidado_dre,
        periodo=periodo_teste_api_comentario_analise_consolidado_dre,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS
    )


@pytest.fixture
def comentario_analise_consolidado_dre_01(consolidado_dre_teste_api_comentario_analise_consolidado_dre):
    return baker.make(
        'ComentarioAnaliseConsolidadoDRE',
        consolidado_dre=consolidado_dre_teste_api_comentario_analise_consolidado_dre,
        ordem=1,
        comentario='Este é um comentario de analise de consolidadodo DRE',
        notificado=False,
        notificado_em=None,
    )


@pytest.fixture
def comentario_analise_consolidado_dre_02(consolidado_dre_teste_api_comentario_analise_consolidado_dre):
    return baker.make(
        'ComentarioAnaliseConsolidadoDRE',
        consolidado_dre=consolidado_dre_teste_api_comentario_analise_consolidado_dre,
        ordem=2,
        comentario='Este é outro comentario de analise de consolidadodo DRE',
        notificado=False,
        notificado_em=None,
    )


@pytest.fixture
def comentario_analise_consolidado_dre_03(consolidado_dre_teste_api_comentario_analise_consolidado_dre):
    return baker.make(
        'ComentarioAnaliseConsolidadoDRE',
        consolidado_dre=consolidado_dre_teste_api_comentario_analise_consolidado_dre,
        ordem=3,
        comentario='Este é mais um comentario de analise de consolidadodo DRE',
        notificado=False,
        notificado_em=None,
    )
