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
def prestacao_conta_2019_2_cartao(periodo_2019_2, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2019_2,
        associacao=associacao,
    )


@pytest.fixture
def prestacao_conta_2020_1_cartao(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@pytest.fixture
def prestacao_conta_2020_1_cheque(periodo_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_2020_1,
        associacao=associacao,
    )


@freeze_time('2020-06-15')
def test_get_periodos_prestacao_de_contas_da_associacao(
    jwt_authenticated_client_a,
    associacao,
    periodo_2019_1,
    periodo_2019_2,
    periodo_2020_1,
    periodo_2020_2,
    prestacao_conta_2019_2_cartao,
    prestacao_conta_2020_1_cartao,
):
    response = jwt_authenticated_client_a.get(f'/api/associacoes/{associacao.uuid}/periodos-para-prestacao-de-contas/',
                          content_type='application/json')
    result = json.loads(response.content)

    esperados = {
        f'{periodo_2019_2.uuid}',
        f'{periodo_2020_1.uuid}',
        f'{periodo_2020_2.uuid}'
    }

    assert response.status_code == status.HTTP_200_OK

    for p in result:
        esperados.discard(p['uuid'])

    assert esperados == set()
