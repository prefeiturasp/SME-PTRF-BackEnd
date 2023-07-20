import pytest

from model_bakery import baker


@pytest.fixture
def motivo_rejeicao():
    return baker.make(
        'MotivoRejeicaoEncerramentoContaAssociacao',
        nome='Pix inválido'
    )

@pytest.fixture
def motivo_rejeicao_2():
    return baker.make(
        'MotivoRejeicaoEncerramentoContaAssociacao',
        nome='Conta inválida'
    )

@pytest.fixture
def payload_motivo_rejeicao_valido():
    payload = {
        'nome': 'Motivo de teste',
    }
    return payload

@pytest.fixture
def payload_motivo_rejeicao_invalido():
    payload = {
        'nome': 'Pix inválido',
    }
    return payload

@pytest.fixture
def payload_update_motivo_rejeicao_valido():
    payload = {
        'nome': 'Pix da conta inválido',
    }
    return payload
