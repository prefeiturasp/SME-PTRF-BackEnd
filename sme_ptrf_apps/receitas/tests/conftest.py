import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def tipo_receita():
    return baker.make('TipoReceita', nome='Estorno')


@pytest.fixture
def tipo_receita_estorno(tipo_receita):
    return tipo_receita


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse')


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


@pytest.fixture
def receita_xxx_estorno(associacao, conta_associacao, acao_associacao, tipo_receita_estorno):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita XXX",
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_estorno,
    )


@pytest.fixture
def receita_yyy_repasse(associacao, conta_associacao, acao_associacao, tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita YYY",
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_repasse,
    )
