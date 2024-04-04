import pytest
from model_bakery import baker
from datetime import date


@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )


@pytest.fixture
def conta_associacao_exportacao_csv(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        banco_nome='Banco do Brasil',
        agencia='12345',
        numero_conta='123456-x',
        numero_cartao='534653264523',
        data_inicio=date(2019, 1, 1)
    )
