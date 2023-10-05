from datetime import date
import pytest
from model_bakery import baker
from ...models import Mandato

pytestmark = pytest.mark.django_db


@pytest.fixture
def mandato_01_2021_a_2022_api():
    return baker.make(
        'Mandato',
        referencia_mandato='2021 a 2022',
        data_inicial=date(2021, 1, 1),
        data_final=date(2022, 12, 31),
    )


@pytest.fixture
def mandato_02_2023_a_2025_api():
    return baker.make(
        'Mandato',
        referencia_mandato='2023 a 2025',
        data_inicial=date(2023, 1, 1),
        data_final=date(2024, 12, 31),
    )


@pytest.fixture
def payload_01_mandato():
    payload = {
        "referencia_mandato": "2026 a 2027",
        "data_inicial": "2026-1-1",
        "data_final": "2027-12-31"
    }
    return payload


@pytest.fixture
def payload_01_mandato_erro_vigencia_outro_mandato():
    payload = {
        "referencia_mandato": "2026 a 2027",
        "data_inicial": "2024-12-31",
        "data_final": "2027-12-31"
    }
    return payload

@pytest.fixture
def payload_02_mandato_erro_vigencia_outro_mandato():
    payload = {
        "referencia_mandato": "2026 a 2027",
        "data_inicial": "2022-12-31",
        "data_final": "2027-12-31"
    }
    return payload


@pytest.fixture
def payload_01_mandato_erro_data_final_maior_que_data_inical():
    payload = {
        "referencia_mandato": "2026 a 2027",
        "data_inicial": "2024-12-31",
        "data_final": "2024-12-30"
    }
    return payload


@pytest.fixture
def payload_01_update_mandato():
    payload = {
        "referencia_mandato": "2028 a 2029",
        "data_inicial": "2028-1-1",
        "data_final": "2029-12-31"
    }
    return payload


@pytest.fixture
def mandato_anterior_01_2021_a_2022_api():
    return baker.make(
        'Mandato',
        referencia_mandato='2021 a 2022',
        data_inicial=date(2021, 1, 1),
        data_final=date(2022, 12, 31),
    )


@pytest.fixture
def composicao_anterior_01_2021_a_2022_api(mandato_anterior_01_2021_a_2022_api, associacao):
    return baker.make(
        'Composicao',
        associacao=associacao,
        mandato=mandato_anterior_01_2021_a_2022_api,
        data_inicial=date(2021, 1, 1),
        data_final=date(2022, 12, 31),
    )
