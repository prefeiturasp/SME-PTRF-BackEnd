import json
from datetime import date

import pytest
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_2019_2(periodo_2019_1):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        periodo_anterior=periodo_2019_1
    )


@pytest.fixture
def periodo_2020_1(periodo_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=periodo_2019_2
    )


@pytest.fixture
def periodo_2020_2(periodo_2020_1):
    return baker.make(
        'Periodo',
        referencia='2020.2',
        data_inicio_realizacao_despesas=date(2020, 7, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=periodo_2020_1
    )


@pytest.fixture
def associacao_teste(unidade, periodo_2019_1):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade,
        periodo_inicial=periodo_2019_1,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@freeze_time('2020-06-15')
def test_get_periodos_prestacao_de_contas_da_associacao(
    jwt_authenticated_client_a,
    associacao_teste,
    periodo_2019_1,
    periodo_2019_2,
    periodo_2020_1,
    periodo_2020_2,
):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao_teste.uuid}/periodos-ate-agora-fora-implantacao/',
        content_type='application/json')

    result = json.loads(response.content)

    esperados = [
        {
            'data_fim_realizacao_despesas': f'{periodo_2020_1.data_fim_realizacao_despesas}',
            'data_inicio_realizacao_despesas': f'{periodo_2020_1.data_inicio_realizacao_despesas}',
            'referencia': '2020.1',
            'referencia_por_extenso': periodo_2020_1.referencia_por_extenso,
            'uuid': f'{periodo_2020_1.uuid}'
        },
        {
            'data_fim_realizacao_despesas': f'{periodo_2019_2.data_fim_realizacao_despesas}',
            'data_inicio_realizacao_despesas': f'{periodo_2019_2.data_inicio_realizacao_despesas}',
            'referencia': '2019.2',
            'referencia_por_extenso': periodo_2019_2.referencia_por_extenso,
            'uuid': f'{periodo_2019_2.uuid}'
        },
    ]

    assert response.status_code == status.HTTP_200_OK

    assert result == esperados
