from datetime import date, timedelta

import pytest
from django.test import RequestFactory
from model_bakery import baker

from sme_ptrf_apps.users.models import User
from sme_ptrf_apps.users.tests.factories import UserFactory
from .core.models import AcaoAssociacao, ContaAssociacao, STATUS_FECHADO
from .despesas.tipos_aplicacao_recurso import APLICACAO_CUSTEIO, APLICACAO_CAPITAL


@pytest.fixture
def fake_user(client, django_user_model, associacao):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password, associacao=associacao)
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


@pytest.fixture
def tipo_receita():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def receita_100_no_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=100.00,
        descricao="Receita 100",
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )


@pytest.fixture
def receita_200_no_inicio_do_periodo(associacao, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas,
        valor=200.00,
        descricao="Receita 200",
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
        descricao="Receita 300",
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
        descricao="Receita 50",
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
        descricao="Receita 30",
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


# rateio_100_custeio
@pytest.fixture
def rateio_no_periodo_100_custeio(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
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
def rateio_no_periodo_200_capital(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_capital,
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
def rateio_no_periodo_10_custeio_outra_acao(associacao, despesa_no_periodo, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
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
def rateio_fora_periodo_50_custeio(associacao, despesa_fora_periodo, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
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
