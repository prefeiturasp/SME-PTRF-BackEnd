import datetime
import json

import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


@freeze_time('2023-04-20 10:11:12')
def test_action_valida_data_de_encerramento_deve_gerar_erro_sem_data_passada(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/validar-data-de-encerramento', follow=True)

    result = json.loads(response.content)

    esperado = {
        'erro': 'parametros_requeridos',
        'mensagem': 'É necessário informar a data de encerramento'
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@freeze_time('2023-04-20 10:11:12')
def test_action_valida_data_de_encerramento_deve_gerar_erro_data_maior_que_hoje(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/validar-data-de-encerramento?data_de_encerramento=2023-10-30', follow=True)

    result = json.loads(response.content)

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Data de encerramento não pode ser maior que a data de Hoje"
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_valida_data_de_encerramento_deve_gerar_erro_data_menor_que_data_periodo_inical(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):

    # data periodo = 2019, 8, 31

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/validar-data-de-encerramento?data_de_encerramento=2019-8-30', follow=True)

    result = json.loads(response.content)

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Data de encerramento não pode ser menor que data_fim_realizacao_despesas do período inicial"
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_valida_data_de_encerramento_deve_gerar_erro_tem_movimentacao(
    jwt_authenticated_client_a,
    associacao,
    periodo_anterior,
    periodo,
    acao_associacao,
    receita_100_no_periodo,
):

    # data periodo = 2019, 8, 31

    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/validar-data-de-encerramento?data_de_encerramento=2019-9-01', follow=True)

    result = json.loads(response.content)

    esperado = {
        "erro": "data_invalida",
        "mensagem": "Existem movimentações cadastradas após a data informada. Favor alterar a data das movimentações ou a data do encerramento."
    }

    assert result == esperado
    assert response.status_code == status.HTTP_400_BAD_REQUEST
