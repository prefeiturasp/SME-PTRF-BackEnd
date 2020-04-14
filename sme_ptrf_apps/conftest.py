from datetime import date

import pytest
from django.test import RequestFactory
from model_bakery import baker

from sme_ptrf_apps.users.models import User
from sme_ptrf_apps.users.tests.factories import UserFactory
from .core.models import AcaoAssociacao, ContaAssociacao, STATUS_FECHADO


@pytest.fixture
def fake_user(client, django_user_model):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password, )
    client.login(username=username, password=password)
    return user


@pytest.fixture
def authenticated_client(client, django_user_model):
    password = 'teste'
    username = 'fake'
    django_user_model.objects.create_user(username=username, password=password, )
    client.login(username=username, password=password)
    return client


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
def acao_role_cultural():
    return baker.make('Acao', nome='Rolê Cultural')

@pytest.fixture
def dre():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE')

@pytest.fixture
def unidade(dre):
    return baker.make('Unidade', codigo_eol='123456', dre=dre, tipo_unidade='CEU', nome='Escola Teste')

@pytest.fixture
def associacao(unidade):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        presidente_associacao_nome='Fulano',
        presidente_associacao_rf='1234567',
        presidente_conselho_fiscal_nome='Ciclano',
        presidente_conselho_fiscal_rf='7654321',
    )


@pytest.fixture
def conta_associacao(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta
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
def periodo():
    return baker.make(
        'Periodo',
        data_inicio_realizacao_despesas=date(2019, 9, 1),
        data_fim_realizacao_despesas=date(2019, 11, 30),
        data_prevista_repasse=date(2019, 10, 1),
        data_inicio_prestacao_contas=date(2019, 12, 1),
        data_fim_prestacao_contas=date(2019, 12, 5)
    )

@pytest.fixture
def periodo_anterior():
    return baker.make(
        'Periodo',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31)
    )

@pytest.fixture
def fechamento_periodo_anterior(periodo_anterior, associacao, conta_associacao, acao_associacao,):
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
        status=STATUS_FECHADO
    )
