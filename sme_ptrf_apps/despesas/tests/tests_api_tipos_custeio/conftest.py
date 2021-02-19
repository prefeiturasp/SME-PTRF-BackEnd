import pytest
from model_bakery import baker


@pytest.fixture
def tipo_custeio_01():
    return baker.make('TipoCusteio', nome='Servico 01')


@pytest.fixture
def tipo_custeio_02():
    return baker.make('TipoCusteio', nome='Servico 02')


@pytest.fixture
def payload_update_tag(tipo_custeio_01):
    payload = {
        'nome': 'Tipo Custeio 01 - Updated',
    }
    return payload
