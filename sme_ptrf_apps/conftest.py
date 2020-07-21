from datetime import date, datetime, timedelta

import pytest
from django.test import RequestFactory
from model_bakery import baker
from rest_framework.test import APIClient

from sme_ptrf_apps.users.models import User
from sme_ptrf_apps.users.tests.factories import UserFactory
from .core.choices import MembroEnum, RepresentacaoCargo
from .core.models import AcaoAssociacao, ContaAssociacao, STATUS_FECHADO, STATUS_ABERTO, STATUS_IMPLANTACAO
from .core.models.prestacao_conta import STATUS_ABERTO as PRESTACAO_ABERTA
from .core.models.prestacao_conta import STATUS_FECHADO as PRESTACAO_FECHADA
from .despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO


@pytest.fixture
def fake_user(client, django_user_model, associacao):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password, associacao=associacao)
    client.login(username=username, password=password)
    return user


@pytest.fixture
def authenticated_client(client, django_user_model, associacao):
    password = 'teste'
    username = 'fake'
    django_user_model.objects.create_user(username=username, password=password, associacao=associacao)
    client.login(username=username, password=password)
    return client


@pytest.fixture
def usuario(associacao):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, associacao=associacao, email=email)
    return user


@pytest.fixture
def jwt_authenticated_client(client, usuario):
    from unittest.mock import patch
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


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def tipo_conta():
    return baker.make('TipoConta', nome='Cheque')


@pytest.fixture
def tipo_conta_cheque(tipo_conta):
    return tipo_conta


@pytest.fixture
def tipo_conta_cartao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def acao():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def acao_ptrf(acao):
    return acao


@pytest.fixture
def acao_de_destaque():
    return baker.make('Acao', nome='ZZZZZ', posicao_nas_pesquisas='AAAAAAAAAA')


@pytest.fixture
def acao_role_cultural():
    return baker.make('Acao', nome='Rolê Cultural')


@pytest.fixture
def dre():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE', nome='DRE teste')


@pytest.fixture
def unidade(dre):
    return baker.make('Unidade', codigo_eol='123456', dre=dre, tipo_unidade='CEU', nome='Escola Teste')


@pytest.fixture
def associacao(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        presidente_associacao_nome='Fulano',
        presidente_associacao_rf='1234567',
        presidente_conselho_fiscal_nome='Ciclano',
        presidente_conselho_fiscal_rf='7654321',
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def outra_associacao(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Outra',
        cnpj='52.302.275/0001-99',
        unidade=unidade,
        presidente_associacao_nome='Fulano',
        presidente_associacao_rf='1234567',
        presidente_conselho_fiscal_nome='Ciclano',
        presidente_conselho_fiscal_rf='7654321',
        periodo_inicial=periodo_anterior,
    )


@pytest.fixture
def associacao_sem_periodo_inicial(unidade):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        presidente_associacao_nome='Fulano',
        presidente_associacao_rf='1234567',
        presidente_conselho_fiscal_nome='Ciclano',
        presidente_conselho_fiscal_rf='7654321',
        periodo_inicial=None,
    )


@pytest.fixture
def conta_associacao(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def conta_associacao_cheque(associacao, tipo_conta_cheque):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cheque
    )


@pytest.fixture
def conta_associacao_cartao(associacao, tipo_conta_cartao):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_cartao
    )


@pytest.fixture
def conta_associacao_inativa(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        status=ContaAssociacao.STATUS_INATIVA
    )


@pytest.fixture
def acao_associacao(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao
    )


@pytest.fixture
def acao_associacao_de_destaque(associacao, acao_de_destaque):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_de_destaque
    )


@pytest.fixture
def acao_associacao_inativa(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status=AcaoAssociacao.STATUS_INATIVA
    )


@pytest.fixture
def acao_associacao_ptrf(associacao, acao_ptrf):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_ptrf
    )


@pytest.fixture
def acao_associacao_role_cultural(associacao, acao_role_cultural):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_role_cultural
    )


@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31)
    )


@pytest.fixture
def periodo(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior
    )


@pytest.fixture
def periodo_aberto(periodo_anterior):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5),
        periodo_anterior=periodo_anterior
    )


@pytest.fixture
def periodo_2020_1(periodo):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def periodo_2019_2(periodo):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 6, 1),
        data_fim_realizacao_despesas=date(2019, 12, 30),
        data_prevista_repasse=date(2019, 6, 1),
        data_inicio_prestacao_contas=date(2020, 1, 1),
        data_fim_prestacao_contas=date(2020, 1, 10),
        periodo_anterior=periodo
    )


@pytest.fixture
def periodo_fim_em_2020_06_30():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_fim_em_aberto():
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2020, 1, 1),
        data_inicio_prestacao_contas=date(2020, 7, 1),
        data_fim_prestacao_contas=date(2020, 7, 10),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_futuro():
    return baker.make(
        'Periodo',
        referencia='2020.3',
        data_inicio_realizacao_despesas=date(2020, 6, 15),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2020, 9, 30),
        data_inicio_prestacao_contas=date(2020, 12, 1),
        data_fim_prestacao_contas=date(2020, 12, 5),
        periodo_anterior=None
    )


@pytest.fixture
def prestacao_conta_anterior(periodo_anterior, associacao, conta_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        prestacao_de_conta_anterior=None,
        status=PRESTACAO_FECHADA,
        conciliado=True
    )


@pytest.fixture
def prestacao_conta(periodo, associacao, conta_associacao, prestacao_conta_anterior):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        prestacao_de_conta_anterior=prestacao_conta_anterior,
        status=PRESTACAO_FECHADA,
        conciliado=True,
        conciliado_em=datetime(2020, 1, 1, 10, 30, 15),
        motivo_reabertura='Teste'
    )


@pytest.fixture
def prestacao_conta_iniciada(periodo_2020_1, associacao, conta_associacao_cartao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        status=PRESTACAO_ABERTA,
        conciliado=False,
        conciliado_em=None,
        motivo_reabertura=''
    )


@pytest.fixture
def fechamento_periodo_anterior(periodo_anterior, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
        total_receitas_livre=2000,
        total_repasses_livre=2000,
        status=STATUS_FECHADO
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada(periodo_2020_1, associacao, conta_associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        status=STATUS_ABERTO,
        conciliado=True,
        conciliado_em=date(2020, 7, 1),
        motivo_reabertura=''
    )


@pytest.fixture
def prestacao_conta_2020_1_conciliada_outra_conta(periodo_2020_1, associacao, conta_associacao_cartao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        status=STATUS_ABERTO,
        conciliado=True,
        conciliado_em=date(2020, 7, 1),
        motivo_reabertura=''
    )


@pytest.fixture
def fechamento_2020_1(periodo_2020_1, associacao, conta_associacao, acao_associacao, prestacao_conta_2020_1_conciliada):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_despesas_nao_conciliadas_capital=8.0,
        total_despesas_nao_conciliadas_custeio=16.0,
        total_receitas_nao_conciliadas_capital=10.0,
        total_receitas_nao_conciliadas_custeio=20.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['cadeira', 'mesa'],
    )


@pytest.fixture
def fechamento_2020_1_outra_conta(periodo_2020_1, associacao, conta_associacao_cartao, acao_associacao,
                                  prestacao_conta_2020_1_conciliada_outra_conta):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_despesas_nao_conciliadas_capital=8.0,
        total_despesas_nao_conciliadas_custeio=16.0,
        total_receitas_nao_conciliadas_capital=10.0,
        total_receitas_nao_conciliadas_custeio=20.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada_outra_conta,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['cadeira', 'mesa'],
    )


@pytest.fixture
def fechamento_periodo_anterior_role(periodo_anterior, associacao, conta_associacao, acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=500,
        total_repasses_capital=450,
        total_despesas_capital=400,
        total_receitas_custeio=1000,
        total_repasses_custeio=900,
        total_despesas_custeio=800,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_anterior_role_implantado(periodo_anterior, associacao, conta_associacao,
                                                acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=2000,
        total_repasses_custeio=0,
        total_despesas_custeio=0,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def fechamento_periodo_anterior_role_implantado_com_livre_aplicacao(periodo_anterior, associacao, conta_associacao,
                                                                    acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=2000,
        total_repasses_custeio=0,
        total_despesas_custeio=0,
        total_receitas_livre=3000,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def fechamento_2020_1_role(periodo_2020_1, associacao, conta_associacao, acao_associacao_role_cultural,
                           prestacao_conta_2020_1_conciliada, fechamento_periodo_anterior_role):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=fechamento_periodo_anterior_role,
        total_receitas_capital=2000,
        total_repasses_capital=1000,
        total_despesas_capital=200,
        total_receitas_custeio=1000,
        total_repasses_custeio=800,
        total_despesas_custeio=100,
        total_despesas_nao_conciliadas_capital=20.0,
        total_despesas_nao_conciliadas_custeio=10.0,
        total_receitas_nao_conciliadas_capital=20.0,
        total_receitas_nao_conciliadas_custeio=10.0,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        especificacoes_despesas_capital=['ar condicionado', ],
        especificacoes_despesas_custeio=['ventilador', 'contador']
    )


@pytest.fixture
def fechamento_periodo_com_saldo(periodo, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=20000,
        total_repasses_capital=20000,
        total_despesas_capital=0,
        total_receitas_custeio=20000,
        total_repasses_custeio=20000,
        total_despesas_custeio=0,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_com_saldo_livre_aplicacao(periodo, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_livre=20000,
        total_repasses_livre=20000,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo_com_saldo_outra_acao(periodo, associacao, conta_associacao, acao_associacao_role_cultural, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        fechamento_anterior=None,
        total_receitas_capital=90000,
        total_repasses_capital=90000,
        total_despesas_capital=0,
        total_receitas_custeio=90000,
        total_repasses_custeio=90000,
        total_despesas_custeio=0,
        status=STATUS_FECHADO
    )


@pytest.fixture
def fechamento_periodo(periodo, associacao, conta_associacao, acao_associacao, fechamento_periodo_anterior):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_periodo_anterior,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        total_receitas_livre=3000,
        total_repasses_livre=3000,
        total_receitas_nao_conciliadas_capital=10,
        total_receitas_nao_conciliadas_custeio=20,
        total_receitas_nao_conciliadas_livre=30,
        total_despesas_nao_conciliadas_capital=8,
        total_despesas_nao_conciliadas_custeio=16,
        status=STATUS_FECHADO,
        especificacoes_despesas_capital=['teste1', 'teste2'],
        especificacoes_despesas_custeio=['teste1', 'teste2'],
    )


@pytest.fixture
def tipo_receita():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def detalhe_tipo_receita_repasse(tipo_receita_repasse):
    return baker.make('DetalheTipoReceita', nome='Repasse YYYÇ', tipo_receita=tipo_receita_repasse)


@pytest.fixture
def detalhe_tipo_receita(tipo_receita):
    return baker.make('DetalheTipoReceita', nome='Estorno A', tipo_receita=tipo_receita)


@pytest.fixture
def receita_100_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )

@pytest.fixture
def receita_1000_no_periodo_livre_aplicacao(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        categoria_receita='LIVRE'
    )



@pytest.fixture
def receita_100_nao_conferida_anterior_ao_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas - timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        conferido=False,
    )


@pytest.fixture
def receita_100_no_periodo_acao_de_destaque(associacao, conta_associacao, acao_associacao_de_destaque, tipo_receita,
                                            periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_de_destaque,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_300_repasse_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita_repasse, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=300.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
    )


@pytest.fixture
def receita_200_no_inicio_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas,
        valor=200.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_300_no_fim_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_fim_realizacao_despesas,
        valor=300.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_50_fora_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        valor=50.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_30_no_periodo_outra_acao(associacao, conta_associacao, acao_associacao_role_cultural, tipo_receita,
                                     periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=30.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe')


@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')


@pytest.fixture
def tipo_aplicacao_recurso_custeio():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_capital():
    return APLICACAO_CAPITAL


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_custeio_material():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def especificacao_material_eletrico(tipo_aplicacao_recurso_custeio, tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
    )


@pytest.fixture
def especificacao_ar_condicionado(tipo_aplicacao_recurso_capital):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Ar condicionado',
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


# despesa_no_periodo
@pytest.fixture
def despesa_no_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor_total=310.00,
        valor_recursos_proprios=0,
    )


@pytest.fixture
def rateio_despesa_demonstrativo(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                 tipo_custeio,
                                 especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'
    )


@pytest.fixture
def rateio_despesa_demonstrativo2(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_custeio, tipo_custeio_material,
                                  especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=200.00,
        quantidade_itens_capital=2,
        valor_item_capital=100.00,
        numero_processo_incorporacao_capital='Teste654321'
    )


# rateio_100_custeio
@pytest.fixture
def rateio_no_periodo_100_custeio(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_custeio,
                                  tipo_custeio_material,
                                  especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00

    )


# rateio_200_capital
@pytest.fixture
def rateio_no_periodo_200_capital(associacao, despesa_no_periodo, conta_associacao, acao,
                                  tipo_aplicacao_recurso_capital,
                                  tipo_custeio,
                                  especificacao_ar_condicionado, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=200.00,
        quantidade_itens_capital=1,
        valor_item_capital=200.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


# rateio_10_custeio_outra_acao
@pytest.fixture
def rateio_no_periodo_10_custeio_outra_acao(associacao, despesa_no_periodo, conta_associacao, acao,
                                            tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_material,
                                            especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_no_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00

    )


# despesa_fora_do_periodo
@pytest.fixture
def despesa_fora_periodo(associacao, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas - timedelta(days=1),
        valor_total=50.00,
        valor_recursos_proprios=0,
    )


# rateio_50_custeio
@pytest.fixture
def rateio_fora_periodo_50_custeio(associacao, despesa_fora_periodo, conta_associacao, acao,
                                   tipo_aplicacao_recurso_custeio,
                                   tipo_custeio_material,
                                   especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_fora_periodo,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=50.00

    )


@pytest.fixture
def parametros():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=True
    )


@pytest.fixture
def parametros_aceita_saldo_negativo_em_conta():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=True
    )


@pytest.fixture
def parametros_nao_aceita_saldo_negativo_em_conta():
    return baker.make(
        'Parametros',
        permite_saldo_conta_negativo=False
    )


@pytest.fixture
def ata_2020_1_cheque_aprovada(prestacao_conta_2020_1_conciliada):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        periodo=prestacao_conta_2020_1_conciliada.periodo,
        associacao=prestacao_conta_2020_1_conciliada.associacao,
        conta_associacao=prestacao_conta_2020_1_conciliada.conta_associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretária',
        comentarios='Teste',
        parecer_conselho='APROVADA'
    )


@pytest.fixture
def ata_prestacao_conta_iniciada(prestacao_conta_iniciada):
    return baker.make(
        'Ata',
        prestacao_conta=prestacao_conta_iniciada,
        periodo=prestacao_conta_iniciada.periodo,
        associacao=prestacao_conta_iniciada.associacao,
        conta_associacao=prestacao_conta_iniciada.conta_associacao,
        tipo_ata='APRESENTACAO',
        tipo_reuniao='ORDINARIA',
        convocacao='PRIMEIRA',
        data_reuniao=date(2020, 7, 1),
        local_reuniao='Escola Teste',
        presidente_reuniao='José',
        cargo_presidente_reuniao='Presidente',
        secretario_reuniao='Ana',
        cargo_secretaria_reuniao='Secretaria',
        comentarios='Teste',
        parecer_conselho='APROVADA'
    )


@pytest.fixture
def membro_associacao(associacao):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao,
        cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.SERVIDOR.value,
        codigo_identificacao='567432'
    )


@pytest.fixture
def payload_membro_servidor(associacao):
    payload = {
        'nome': "Adriano Imperador",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name,
        'cargo_educacao': 'Coordenador',
        'representacao': RepresentacaoCargo.SERVIDOR.name,
        'codigo_identificacao': '567432'
    }
    return payload


@pytest.fixture
def payload_membro_estudante(associacao):
    payload = {
        'nome': "Arthur Oliveira",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.VOGAL_1.name,
        'cargo_educacao': '',
        'representacao': RepresentacaoCargo.ESTUDANTE.name,
        'codigo_identificacao': '567431'
    }
    return payload


@pytest.fixture
def payload_membro_pai_responsavel(associacao):
    payload = {
        'nome': "Lana Oliveira",
        'associacao': str(associacao.uuid),
        'cargo_associacao': MembroEnum.VOGAL_3.name,
        'cargo_educacao': '',
        'representacao': RepresentacaoCargo.PAI_RESPONSAVEL.name,
        'codigo_identificacao': ''
    }
    return payload


@pytest.fixture
def observacao(acao_associacao, prestacao_conta):
    return baker.make(
        'Observacao',
        prestacao_conta=prestacao_conta,
        acao_associacao=acao_associacao,
        texto="Uma bela observação."
    )
