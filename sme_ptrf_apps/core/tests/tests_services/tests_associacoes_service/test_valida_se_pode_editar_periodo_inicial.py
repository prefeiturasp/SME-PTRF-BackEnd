import datetime
from datetime import date

import pytest
from model_bakery import baker

from rest_framework import status

from sme_ptrf_apps.core.services.associacoes_service import ValidaSePodeEditarPeriodoInicial

pytestmark = pytest.mark.django_db



@pytest.fixture
def receita_100_no_periodo_02(associacao_02_02, conta_associacao, acao_associacao, tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao_02_02,
        data=periodo.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )

@pytest.fixture
def despesa_100_no_periodo02(associacao_02_02, tipo_documento, tipo_transacao, periodo):
    return baker.make(
        'Despesa',
        associacao=associacao_02_02,
        numero_documento='123456',
        data_documento=periodo.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=periodo.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        valor_total=100.00,
    )

@pytest.fixture
def rateio_despesa_100_no_periodo02(associacao_02_02, despesa_100_no_periodo02, conta_associacao, acao, tipo_aplicacao_recurso_custeio, tipo_custeio_material, especificacao_material_eletrico, acao_associacao):
    return baker.make(
        'RateioDespesa',
        despesa=despesa_100_no_periodo02,
        associacao=associacao_02_02,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00,
        valor_original=100.00,
        quantidade_itens_capital=1,
        valor_item_capital=100.00
    )


@pytest.fixture
def periodo_anterior_sem_fim_realizacao_despesas_02():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
    )

@pytest.fixture
def associacao_02_02(unidade, periodo_anterior_sem_fim_realizacao_despesas_02):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='02.214.687/0001-93',
        unidade=unidade,
        periodo_inicial=periodo_anterior_sem_fim_realizacao_despesas_02,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
        status_valores_reprogramados='NAO_FINALIZADO'
    )

def test_valida_se_pode_editar_periodo_inicial_deve_retornar_true(associacao_02_02):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao_02_02).response

    esperado = {
        "pode_editar_periodo_inicial": True,
        "mensagem_pode_editar_periodo_inicial": [],
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
    }

    assert response == esperado

def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_valores_reprogramados(associacao):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao).response

    esperado = {
        "pode_editar_periodo_inicial": False,
        "mensagem_pode_editar_periodo_inicial": [
            "Não é permitido alterar o período inicial da Associação.",
            "Há cadastros já realizados pela Associação no primeiro período de uso do sistema:",
            "- Valores Reprogramados",
        ],
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
    }

    assert response == esperado


def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_tem_pc(associacao, prestacao_conta_anterior):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao).response

    assert response["pode_editar_periodo_inicial"] == False
    assert "- Prestação de Contas" in response["mensagem_pode_editar_periodo_inicial"]


def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_tem_creditos(
    associacao_02_02,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo_02
):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao_02_02).response

    assert response["pode_editar_periodo_inicial"] == False
    assert "- Crédito(s)" in response["mensagem_pode_editar_periodo_inicial"]


def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_tem_gastos(
    associacao_02_02,
    periodo_anterior,
    periodo,
    acao_associacao,
    rateio_despesa_100_no_periodo02,
):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao_02_02).response

    assert response["pode_editar_periodo_inicial"] == False
    assert "- Despesa(s)" in response["mensagem_pode_editar_periodo_inicial"]


