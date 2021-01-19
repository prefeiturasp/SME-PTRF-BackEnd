import json

import pytest
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_verifica_datas_periodo(
    jwt_authenticated_client_a,
    periodo_2021_2,
):

    response = jwt_authenticated_client_a.get(
        f'/api/periodos/verificar-datas/'
        f'?data_inicio_realizacao_despesas=2021-07-01&data_fim_realizacao_despesas=2021-09-30'
        f'&periodo_anterior_uuid={periodo_2021_2.uuid}'
    )

    result = json.loads(response.content)

    esperado = {
        "valido": True,
        "mensagem": "Período de realização de despesas válido.",
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_verifica_datas_invertidas(
    jwt_authenticated_client_a,
):

    response = jwt_authenticated_client_a.get(
        f'/api/periodos/verificar-datas/'
        f'?data_inicio_realizacao_despesas=2021-09-30&data_fim_realizacao_despesas=2021-07-01'
        f'&periodo_anterior_uuid='
    )

    result = json.loads(response.content)

    esperado = {
        "valido": False,
        "mensagem": "Data fim de realização de despesas precisa ser posterior à data de início.",
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_verifica_datas_descontinuas(
    jwt_authenticated_client_a,
    periodo_2021_2,
):

    response = jwt_authenticated_client_a.get(
        f'/api/periodos/verificar-datas/'
        f'?data_inicio_realizacao_despesas=2021-07-02&data_fim_realizacao_despesas=2021-09-30'
        f'&periodo_anterior_uuid={periodo_2021_2.uuid}'
    )

    result = json.loads(response.content)

    esperado = {
        "valido": False,
        "mensagem": ("Data início de realização de despesas precisa ser imediatamente posterior"
                     " à data de fim do período anterior."),
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_verifica_datas_periodo_anterior_aberto(
    jwt_authenticated_client_a,
    periodo_2021_2_aberto,
):

    response = jwt_authenticated_client_a.get(
        f'/api/periodos/verificar-datas/'
        f'?data_inicio_realizacao_despesas=2021-07-02&data_fim_realizacao_despesas=2021-09-30'
        f'&periodo_anterior_uuid={periodo_2021_2_aberto.uuid}'
    )

    result = json.loads(response.content)

    esperado = {
        "valido": False,
        "mensagem": "Períodos abertos são podem ser selecionados como anterior à um período.",
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


def test_verifica_datas_periodo_anterior_nula_sem_ser_periodo_unico(
    jwt_authenticated_client_a,
    periodo_2021_2,
):

    response = jwt_authenticated_client_a.get(
        f'/api/periodos/verificar-datas/'
        f'?data_inicio_realizacao_despesas=2021-07-02&data_fim_realizacao_despesas=2021-09-30'
        f'&periodo_anterior_uuid='
        f'&periodo_uuid='
    )

    result = json.loads(response.content)

    esperado = {
        "valido": False,
        "mensagem": "Período anterior não definido só é permitido para o primeiro período cadastrado.",
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado

