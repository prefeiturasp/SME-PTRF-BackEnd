import datetime
from datetime import date

import pytest
from model_bakery import baker

from rest_framework import status

from sme_ptrf_apps.core.services.associacoes_service import ValidaDataDeEncerramento

pytestmark = pytest.mark.django_db

@pytest.fixture
def periodo_anterior_sem_fim_realizacao_despesas():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
    )

@pytest.fixture
def associacao_02(unidade, periodo_anterior_sem_fim_realizacao_despesas):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='02.214.687/0001-93',
        unidade=unidade,
        periodo_inicial=periodo_anterior_sem_fim_realizacao_despesas,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456'
    )


def test_valida_data_de_encerramento_deve_gerar_erro_data_maior_que_hoje(
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):
    data_de_encerramento = '2023-10-30'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento).response

    esperado = {
        'erro': 'data_invalida',
        'mensagem': 'Data de encerramento não pode ser maior que a data de Hoje',
        "status": status.HTTP_400_BAD_REQUEST,
    }

    assert response == esperado

def test_valida_data_de_encerramento_deve_gerar_erro_data_menor_que_data_periodo_inicial(
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):
    # data periodo = 2019, 8, 31
    data_de_encerramento = '2019-08-30'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento).response

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial",
        "status": status.HTTP_400_BAD_REQUEST,
    }

    assert response == esperado


def test_valida_data_de_encerramento_deve_gerar_erro_data_menor_que_data_periodo_inicial_passando_parametro_periodo_inicial(
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):
    # data periodo = 2019, 8, 31
    data_de_encerramento = '2019-08-30'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento, periodo_inicial=periodo_anterior).response

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial",
        "status": status.HTTP_400_BAD_REQUEST,
    }

    assert response == esperado


def test_valida_data_de_encerramento_deve_passar_data_maior_que_data_periodo_inicial_passando_parametro_periodo_inicial(
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
):
    # data periodo = 2019, 8, 31
    data_de_encerramento = '2019-09-01'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento, periodo_inicial=periodo_anterior).response

    esperado = {
        'erro': 'data_valida',
        'mensagem': 'Data de encerramento válida',
        "status": status.HTTP_200_OK,
    }

    assert response == esperado


def test_valida_data_de_encerramento_deve_gerar_erro_tem_movimentacao(
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_teste_valida_data_de_encerramento,
):
    data_de_encerramento = '2023-04-20'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao, data_de_encerramento=data_de_encerramento).response

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Existem movimentações cadastradas após a data informada. Favor alterar a data das movimentações ou a data do encerramento.",
        "status": status.HTTP_400_BAD_REQUEST,
    }

    assert response == esperado


def test_valida_data_de_encerramento_periodo_sem_fim(
    associacao_02,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_teste_valida_data_de_encerramento_associacao_02,
):
    data_de_encerramento = '2023-04-20'
    data_de_encerramento = datetime.datetime.strptime(data_de_encerramento, '%Y-%m-%d')
    data_de_encerramento = data_de_encerramento.date()

    response = ValidaDataDeEncerramento(associacao=associacao_02, data_de_encerramento=data_de_encerramento).response

    esperado = {
        'erro': 'data_invalida',
        'mensagem': 'Existem movimentações cadastradas após a data informada. Favor alterar a data das movimentações ou a data do encerramento.',
        "status": status.HTTP_400_BAD_REQUEST,
    }

    assert response == esperado
