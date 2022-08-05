import pytest

from model_bakery import baker
from datetime import date, timedelta

@pytest.fixture
def parametros_dre_valores_reprogramados(tipo_conta, tipo_conta_cartao):
    return baker.make(
        'ParametrosDre',
        tipo_conta_um=tipo_conta,
        tipo_conta_dois=tipo_conta_cartao
    )


@pytest.fixture
def unidade_valores_reprogramados(dre):
    return baker.make(
        'Unidade',
        nome='Duarte',
        tipo_unidade='EMEF',
        codigo_eol='123457',
        dre=dre,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-87',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def valores_reprogramados_valores_corretos(associacao_2, conta_associacao, acao_associacao_aceita_custeio):
    return baker.make(
        'ValoresReprogramados',
        associacao=associacao_2,
        periodo=associacao_2.periodo_inicial,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_aceita_custeio,
        aplicacao_recurso="CUSTEIO",
        valor_ue=0.10,
        valor_dre=0.20
    )


@pytest.fixture
def associacao_2(unidade_valores_reprogramados, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Antonio',
        cnpj='52.302.275/0001-84',
        unidade=unidade_valores_reprogramados,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_3(unidade_valores_reprogramados, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Antonio',
        cnpj='52.302.275/0001-87',
        unidade=unidade_valores_reprogramados,
        periodo_inicial=None,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def fechamento_conta_cheque_valores_reprogramados(periodo_anterior, associacao, conta_associacao_cheque, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=1000,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        status='IMPLANTACAO',
    )

@pytest.fixture
def fechamento_conta_cheque_valores_reprogramados_2(periodo_anterior, associacao_2, conta_associacao_cheque, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao_2,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=700,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        status='IMPLANTACAO',
    )



@pytest.fixture
def fechamento_conta_cartao_valores_reprogramados(periodo_anterior, associacao, conta_associacao_cartao, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
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
        status='IMPLANTACAO',
    )

@pytest.fixture
def fechamento_conta_cartao_valores_reprogramados_2(periodo_anterior, associacao_2, conta_associacao_cartao, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_anterior,
        associacao=associacao_2,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=800,
        total_repasses_capital=900,
        total_despesas_capital=800,
        total_receitas_custeio=2000,
        total_repasses_custeio=1800,
        total_despesas_custeio=1600,
        status='IMPLANTACAO',
    )
