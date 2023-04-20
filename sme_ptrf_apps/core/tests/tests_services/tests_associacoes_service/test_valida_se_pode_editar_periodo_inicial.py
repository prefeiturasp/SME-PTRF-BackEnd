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
        "mensagem_pode_editar_periodo_inicial": "",
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
    }

    assert response == esperado

def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_valores_reprogramados(associacao):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao).response

    esperado = {
        "pode_editar_periodo_inicial": False,
        "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial da Associação, pois há valores reprogramados cadastrados conferidos como corretos no início de uso do sistema.",
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
    }

    assert response == esperado


def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_tem_pc(associacao, prestacao_conta_anterior):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao).response

    esperado = {
        "pode_editar_periodo_inicial": False,
        "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial da Associação, pois há valores reprogramados cadastrados conferidos como corretos no início de uso do sistema.",
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado.",
    }

    assert response == esperado


def test_valida_se_pode_editar_periodo_inicial_deve_retornar_erro_tem_movimentacao(
    associacao_02_02,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo_02
):
    response = ValidaSePodeEditarPeriodoInicial(associacao=associacao_02_02).response

    esperado = {
        "pode_editar_periodo_inicial": False,
        "mensagem_pode_editar_periodo_inicial": "Não é permitido alterar o período inicial pois já houve movimentação após o início de uso do sistema.",
        "help_text": "O período inicial informado é uma referência e indica que o período a ser habilitado para a associação será o período posterior ao período informado."
    }

    assert response == esperado


