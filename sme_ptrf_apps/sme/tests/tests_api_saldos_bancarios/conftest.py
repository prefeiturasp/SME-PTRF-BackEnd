from datetime import date

import pytest

from model_bakery import baker

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_anterior_saldos_bancarios():
    return baker.make(
        'core.Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
    )


@pytest.fixture
def periodo_saldos_bancarios(periodo_anterior_saldos_bancarios):
    return baker.make(
        'core.Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=None,
        data_inicio_prestacao_contas=None,
        data_fim_prestacao_contas=None,
        periodo_anterior=periodo_anterior_saldos_bancarios,
    )


@pytest.fixture
def tipo_conta_saldos_bancarios():
    return baker.make(
        'core.TipoConta', nome='Cartão'
    )


@pytest.fixture
def conta_associacao_saldos_bancarios(associacao, tipo_conta_saldos_bancarios):
    return baker.make(
        'core.ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_saldos_bancarios,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def dre_saldos_bancarios():
    return baker.make('Unidade', codigo_eol='99998', tipo_unidade='DRE', nome='DRE teste2', sigla='TO')

@pytest.fixture
def unidade_saldos_bancarios(dre_saldos_bancarios):
    return baker.make(
        'core.Unidade',
        nome='Escola Teste2',
        tipo_unidade='CEU',
        codigo_eol='123457',
        dre=dre_saldos_bancarios,
        sigla='ET',
    )


@pytest.fixture
def associacao_saldos_bancarios(unidade_saldos_bancarios, periodo_saldos_bancarios):
    return baker.make(
        'core.Associacao',
        nome='Escola Teste',
        cnpj='58.706.452/0001-73',
        unidade=unidade_saldos_bancarios,
        periodo_inicial=periodo_saldos_bancarios,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def observacao_conciliacao_saldos_bancarios(jwt_authenticated_client, associacao_saldos_bancarios,
                                            periodo_saldos_bancarios, conta_associacao_saldos_bancarios):
    return baker.make(
        'core.ObservacaoConciliacao',
        periodo=periodo_saldos_bancarios,
        associacao=associacao_saldos_bancarios,
        conta_associacao=conta_associacao_saldos_bancarios,
        texto="Uma bela observação.",
        data_extrato=None,
        saldo_extrato=1000
    )

