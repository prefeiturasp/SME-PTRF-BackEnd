import pytest


@pytest.fixture
def conta_associacao_1(conta_associacao_factory):
    return conta_associacao_factory.create()


@pytest.fixture
def conta_associacao_2(conta_associacao_factory):
    return conta_associacao_factory.create()


@pytest.fixture
def associacao_1(associacao_factory):
    return associacao_factory.create()


@pytest.fixture
def tipo_conta_1(tipo_conta_factory):
    return tipo_conta_factory.create()
