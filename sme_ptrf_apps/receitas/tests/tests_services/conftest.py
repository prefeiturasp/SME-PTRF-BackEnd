from datetime import date
import pytest
from model_bakery import baker


@pytest.fixture
def periodo_2022_teste_periodo(periodo_2021_teste_periodo):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_2021_teste_periodo,
    )



@pytest.fixture
def periodo_2021_teste_periodo(periodo_2020_teste_periodo):
    return baker.make(
        'Periodo',
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 12, 31),
        periodo_anterior=periodo_2020_teste_periodo,
    )

@pytest.fixture
def periodo_2020_teste_periodo(periodo_anterior_teste_periodo):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        periodo_anterior=periodo_anterior_teste_periodo,
    )


@pytest.fixture
def periodo_anterior_teste_periodo():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
    )


@pytest.fixture
def associacao_sem_data_de_encerramento_teste_periodo(unidade, periodo_anterior_teste_periodo):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='34.845.266/0001-57',
        unidade=unidade,
        periodo_inicial=periodo_anterior_teste_periodo,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
    )



@pytest.fixture
def associacao_com_data_de_encerramento_teste_periodo_02_01_2020(unidade, periodo_anterior_teste_periodo):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='34.845.266/0001-57',
        unidade=unidade,
        periodo_inicial=periodo_anterior_teste_periodo,
        ccm='0.000.00-0',
        email="ollyverottoboni2@gmail.com",
        processo_regularidade='123456',
        data_de_encerramento=date(2020, 1, 2),
    )
