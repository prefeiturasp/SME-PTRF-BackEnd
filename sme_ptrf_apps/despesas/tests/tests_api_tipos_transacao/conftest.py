import pytest
from model_bakery import baker


@pytest.fixture
def tipo_transacao_01():
    return baker.make('TipoTransacao', nome='Cheque')


@pytest.fixture
def tipo_transacao_02():
    return baker.make('TipoTransacao', nome='Cartão')


@pytest.fixture
def payload_update_tag(tipo_transacao_01):
    payload = {
        'nome': 'Pix',
    }
    return payload
