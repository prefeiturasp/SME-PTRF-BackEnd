import pytest
import datetime

from model_bakery import baker


@pytest.fixture
def tipo_receita():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def receita(associacao, conta_associacao, acao_associacao, tipo_receita):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Uma receita",
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
    )

@pytest.fixture
def payload_receita(associacao, conta_associacao, acao_associacao, tipo_receita):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2020-03-26',
        'valor': 100.00,
        'descricao': 'Uma receita',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita.id
    }
    return payload
