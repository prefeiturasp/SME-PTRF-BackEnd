from datetime import date

import pytest

from model_bakery import baker
from sme_ptrf_apps.core.models import SolicitacaoEncerramentoContaAssociacao, ContaAssociacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_anterior_saldos_bancarios(periodo_factory):
    return periodo_factory(
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
    )


@pytest.fixture
def periodo_saldos_bancarios(periodo_factory, periodo_anterior_saldos_bancarios):
    return periodo_factory(
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=None,
        data_inicio_prestacao_contas=None,
        data_fim_prestacao_contas=None,
        periodo_anterior=periodo_anterior_saldos_bancarios,
    )

@pytest.fixture
def periodo_posterior_saldos_bancarios(periodo_factory, periodo_saldos_bancarios):
    return periodo_factory(
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 7, 1),
        data_prevista_repasse=None,
        data_inicio_prestacao_contas=None,
        data_fim_prestacao_contas=None,
        periodo_anterior=periodo_saldos_bancarios,
    )


@pytest.fixture
def tipo_conta_saldos_bancarios():
    return baker.make(
        'core.TipoConta', nome='Cartão'
    )


@pytest.fixture
def conta_associacao_saldos_bancarios(associacao_saldos_bancarios, tipo_conta_saldos_bancarios):
    return baker.make(
        'core.ContaAssociacao',
        associacao=associacao_saldos_bancarios,
        tipo_conta=tipo_conta_saldos_bancarios,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523'
    )


@pytest.fixture
def conta_associacao_saldos_bancarios_iniciada_em_2021_1(associacao_saldos_bancarios, tipo_conta_saldos_bancarios, periodo_posterior_saldos_bancarios):
    return baker.make(
        'core.ContaAssociacao',
        associacao=associacao_saldos_bancarios,
        tipo_conta=tipo_conta_saldos_bancarios,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        data_inicio=periodo_posterior_saldos_bancarios.data_inicio_realizacao_despesas
    )


@pytest.fixture
def conta_associacao_saldos_bancarios_encerrada_em_2020_1(associacao_saldos_bancarios, tipo_conta_saldos_bancarios):
    return baker.make(
        'core.ContaAssociacao',
        associacao=associacao_saldos_bancarios,
        tipo_conta=tipo_conta_saldos_bancarios,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        status=ContaAssociacao.STATUS_INATIVA
    )

@pytest.fixture
def solicitacao_encerramento_conta_aprovada(conta_associacao_saldos_bancarios_encerrada_em_2020_1, periodo_anterior_saldos_bancarios):
    return baker.make(
        'SolicitacaoEncerramentoContaAssociacao',
        conta_associacao=conta_associacao_saldos_bancarios_encerrada_em_2020_1,
        status=SolicitacaoEncerramentoContaAssociacao.STATUS_APROVADA,
        data_de_encerramento_na_agencia=periodo_anterior_saldos_bancarios.data_inicio_realizacao_despesas,
        data_aprovacao=periodo_anterior_saldos_bancarios.data_inicio_realizacao_despesas
    )


@pytest.fixture
def dre_saldos_bancarios():
    return baker.make('Unidade', codigo_eol='99998', tipo_unidade='DRE', nome='DRE teste2', sigla='TO')


@pytest.fixture
def dre():
    return baker.make('Unidade', codigo_eol='99999', tipo_unidade='DRE', nome='DRE teste', sigla='TT')


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

@pytest.fixture
def observacao_conciliacao_saldos_bancarios_com_conta_nao_iniciada(jwt_authenticated_client, associacao_saldos_bancarios,
                                                                   periodo_saldos_bancarios, conta_associacao_saldos_bancarios_iniciada_em_2021_1):
    return baker.make(
        'core.ObservacaoConciliacao',
        periodo=periodo_saldos_bancarios,
        associacao=associacao_saldos_bancarios,
        conta_associacao=conta_associacao_saldos_bancarios_iniciada_em_2021_1,
        texto="Uma bela observação de uma conta que não foi iniciada.",
        data_extrato=None,
        saldo_extrato=1000
    )


@pytest.fixture
def observacao_conciliacao_saldos_bancarios_com_conta_encerrada(jwt_authenticated_client, associacao_saldos_bancarios,
                                                                   periodo_saldos_bancarios, conta_associacao_saldos_bancarios_encerrada_em_2020_1):
    return baker.make(
        'core.ObservacaoConciliacao',
        periodo=periodo_saldos_bancarios,
        associacao=associacao_saldos_bancarios,
        conta_associacao=conta_associacao_saldos_bancarios_encerrada_em_2020_1,
        texto="Uma bela observação de uma conta que já foi encerrada.",
        data_extrato=None,
        saldo_extrato=1000
    )


