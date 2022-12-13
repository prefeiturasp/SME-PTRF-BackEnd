from datetime import date, datetime, timedelta
from freezegun import freeze_time
import pytest
from model_bakery import baker
from sme_ptrf_apps.dre.models import ConsolidadoDRE, TecnicoDre
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
def dre_teste_service_notificacao_analise_consolidado_dre():
    return baker.make(
        'Unidade',
        codigo_eol='108599',
        tipo_unidade='DRE',
        nome='Dre Teste Notificação Análise Consolidado DRE',
        sigla='A'
    )


@pytest.fixture
def dre_teste_service_notificacao_analise_consolidado_dre_nao_eh_a_dre_do_membro():
    return baker.make(
        'Unidade',
        codigo_eol='108699',
        tipo_unidade='DRE',
        nome='Dre Teste Notificação Análise Consolidado DRE Não é a DRE do Comentário',
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
                                                                 dre_teste_service_notificacao_analise_consolidado_dre):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
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

@pytest.fixture
def comissao_exame_contas_teste_service():
    return baker.make('Comissao', nome='Exame de Contas')


@pytest.fixture
def comissao_nao_exame_contas_teste_service():
    return baker.make('Comissao', nome='NÃO Exame de Contas')


@pytest.fixture
def parametros_dre_teste_service(comissao_exame_contas_teste_service):
    return baker.make(
        'ParametrosDre',
        comissao_exame_contas=comissao_exame_contas_teste_service
    )


@pytest.fixture
def membro_comissao_teste_service(comissao_exame_contas_teste_service, dre_teste_service_notificacao_analise_consolidado_dre):
    membro = baker.make(
        'MembroComissao',
        rf='1235678',
        nome='Beto',
        cargo='teste',
        email='beto@teste.com',
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
        comissoes=[comissao_exame_contas_teste_service]
    )
    return membro

@pytest.fixture
def nao_membro_comissao_de_exame_teste_service(comissao_nao_exame_contas_teste_service, dre_teste_service_notificacao_analise_consolidado_dre):
    membro = baker.make(
        'MembroComissao',
        rf='1235678',
        nome='Beto',
        cargo='teste',
        email='beto@teste.com',
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
        comissoes=[comissao_nao_exame_contas_teste_service]
    )
    return membro


@pytest.fixture
def periodo_2021_4_pc_2021_06_18_a_2021_06_30():
    return baker.make(
        'Periodo',
        referencia='2021.4',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 6, 18),
        data_fim_prestacao_contas=date(2021, 6, 30),
        periodo_anterior=None,
        notificacao_inicio_periodo_pc_realizada=False
    )


@pytest.fixture
def membro_comissao_outra_dre_nao_deve_notificar_teste_service(
    comissao_exame_contas_teste_service,
    dre_teste_service_notificacao_analise_consolidado_dre
):
    membro = baker.make(
        'MembroComissao',
        rf='1235678',
        nome='Beto',
        cargo='teste',
        email='beto@teste.com',
        dre=dre_teste_service_notificacao_analise_consolidado_dre,
        comissoes=[comissao_exame_contas_teste_service]
    )
    return membro


@pytest.fixture
def unidade_a(dre):
    return baker.make(
        'Unidade',
        nome='Escola A',
        tipo_unidade='EMEI',
        codigo_eol='270001',
        dre=dre,
        sigla='EA'
    )


@pytest.fixture
def associacao_a(unidade_a):
    return baker.make(
        'Associacao',
        nome='Associacao 271170',
        cnpj='62.738.735/0001-74',
        unidade=unidade_a,
    )


@pytest.fixture
def visao_dre():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def usuario_notificavel(
    unidade_a,
    visao_dre):
    from django.contrib.auth import get_user_model

    senha = 'Sgp0418'
    login = '2711001'
    email = 'notificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_a)
    user.visoes.add(visao_dre)
    user.save()
    return user


@pytest.fixture
def usuario_tecnico_notificavel():
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '5047951'
    email = 'notificavel@amcom.com.br'

    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.save()
    return user

@pytest.fixture
def tecnico_notificavel(unidade_a, visao_dre, dre, usuario_tecnico_notificavel):
    email = 'notificavel@amcom.com.br'
    tecnico = TecnicoDre.objects.create(
        nome='MARIA DO CARMO MACHADO LEAL DE GODOY',
        dre=dre,
        rf='5047951',
        email=email,
        telefone='1938342667'
    )
    tecnico.save()
    return tecnico


@pytest.fixture
def periodo_anterior_teste_service_consolidado_dre():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_service_consolidado_dre(periodo_anterior_teste_service_consolidado_dre):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_service_consolidado_dre,
    )

@pytest.fixture
@freeze_time("2022-10-21")
def analise_consolidado_dre_01_prazo_acerto_vencido():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=datetime.now() - timedelta(days = 1 ),
        data_limite=datetime.now() - timedelta(days = 1 ),
        data_retorno_analise=datetime.now() - timedelta(days = 1 ),
        copiado=False
    )


@pytest.fixture
def analise_consolidado_dre_01_dentro_prazo():
    return baker.make(
        'AnaliseConsolidadoDre',
        data_devolucao=datetime.now(),
        data_limite=datetime.now(),
        data_retorno_analise=datetime.now(),
    )


@pytest.fixture
def consolidado_dre_devolucao_apos_acertos(periodo_teste_service_consolidado_dre, dre, analise_consolidado_dre_01_prazo_acerto_vencido, tecnico_notificavel):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo_teste_service_consolidado_dre,
        status_sme=ConsolidadoDRE.STATUS_SME_DEVOLVIDO,
        analise_atual=analise_consolidado_dre_01_prazo_acerto_vencido,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def consolidado_dre_devolucao_apos_acertos_dentro_do_prazo(periodo_teste_service_consolidado_dre, dre, analise_consolidado_dre_01_dentro_prazo, tecnico_notificavel):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo_teste_service_consolidado_dre,
        status_sme=ConsolidadoDRE.STATUS_SME_DEVOLVIDO,
        analise_atual=analise_consolidado_dre_01_dentro_prazo,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )


@pytest.fixture
def consolidado_dre_devolucao_apos_acertos_em_analise(periodo_teste_service_consolidado_dre, dre, analise_consolidado_dre_01_dentro_prazo, tecnico_notificavel):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo_teste_service_consolidado_dre,
        status_sme=ConsolidadoDRE.STATUS_SME_EM_ANALISE,
        analise_atual=analise_consolidado_dre_01_dentro_prazo,
        eh_parcial=False,
        sequencia_de_publicacao=0
    )

