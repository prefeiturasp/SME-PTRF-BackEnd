import pytest

from model_bakery import baker


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe')


@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')
