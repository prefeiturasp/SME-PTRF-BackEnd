import pytest

from datetime import date
from model_bakery import baker


@pytest.fixture
def periodo_2020_4():
    return baker.make(
        'Periodo',
        referencia='2020.4',
        data_inicio_realizacao_despesas=date(2020, 10, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=date(2020, 10, 1),
        data_inicio_prestacao_contas=date(2021, 1, 1),
        data_fim_prestacao_contas=date(2021, 1, 15),
        periodo_anterior=None,
    )


@pytest.fixture
def periodo_2021_1(periodo_2020_4):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 3, 31),
        data_prevista_repasse=date(2021, 1, 1),
        data_inicio_prestacao_contas=date(2021, 4, 1),
        data_fim_prestacao_contas=date(2021, 4, 15),
        periodo_anterior=periodo_2020_4,
    )


@pytest.fixture
def periodo_2021_2(periodo_2021_1):
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=periodo_2021_1,
    )

