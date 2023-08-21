from datetime import date
import pytest
from model_bakery import baker

pytestmark = pytest.mark.django_db

@pytest.fixture
def mandato_2023_a_2025():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20),
    )

@pytest.fixture
def mandato_2023_a_2025_testes_servicos_01():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 8, 8),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def mandato_2023_a_2025_testes_servicos_02():
    return baker.make(
        'Mandato',
        referencia_mandato='2026 a 2028',
        data_inicial=date(2023, 7, 19),
        data_final=date(2023, 7, 20),
    )

@pytest.fixture
def composicao_01_2023_a_2025_testes_servicos(mandato_2023_a_2025_testes_servicos_01, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_servicos_01,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def composicao_02_2023_a_2025_testes_servicos(mandato_2023_a_2025_testes_servicos_01, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025_testes_servicos_01,
        data_inicial=date(2026, 1, 1),
        data_final=date(2028, 12, 31),
    )

@pytest.fixture
def composicao_01_2023_a_2025(mandato_2023_a_2025, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )

@pytest.fixture
def composicao_02_2023_a_2025(mandato_2023_a_2025, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_2023_a_2025,
        data_inicial=date(2023, 1, 1),
        data_final=date(2025, 12, 31),
    )


@pytest.fixture
def ocupante_cargo_01():
    return baker.make(
        'OcupanteCargo',
        nome="Ollyver Ottoboni",
        codigo_identificacao='1234567',
        cargo_educacao="Diretor de Escola",
        representacao='Servidor',
        email='ottoboniollyver@gmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Aeroporto',
        endereco='Rua do ocupante, 212',
    )

@pytest.fixture
def ocupante_cargo_02():
    return baker.make(
        'OcupanteCargo',
        nome="Ollyver Ottoboni 02",
        codigo_identificacao='754321',
        cargo_educacao="Diretor de Escola 02",
        representacao='Servidor',
        email='ottoboniollyver@gmail.com',
        cpf_responsavel='907.536.560-86',
        telefone='11976643126',
        cep='02847070',
        bairro='Jd. Aeroporto',
        endereco='Rua do ocupante, 212',
    )


@pytest.fixture
def cargo_composicao_01(
    composicao_01_2023_a_2025,
    ocupante_cargo_01,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025,
        ocupante_do_cargo=ocupante_cargo_01,
        cargo_associacao='Presidente da diretoria executiva',
        substituto=False,
        substituido=False,
    )

@pytest.fixture
def cargo_composicao_01_testes_services(
    composicao_01_2023_a_2025_testes_servicos,
    ocupante_cargo_01,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025_testes_servicos,
        ocupante_do_cargo=ocupante_cargo_01,
        cargo_associacao='PRESIDENTE_DIRETORIA_EXECUTIVA',
        substituto=False,
        substituido=False,
    )

@pytest.fixture
def cargo_composicao_02(
    composicao_01_2023_a_2025,
    ocupante_cargo_02,
):
    return baker.make(
        'CargoComposicao',
        composicao=composicao_01_2023_a_2025,
        ocupante_do_cargo=ocupante_cargo_02,
        cargo_associacao='Vice Presidente da diretoria executiva',
        substituto=False,
        substituido=False,
    )
