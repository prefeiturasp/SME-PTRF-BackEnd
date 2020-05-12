import datetime

import pytest
from model_bakery import baker


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)

@pytest.fixture
def receita_2020_1_role_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural, tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
    )

@pytest.fixture
def receita_2020_1_role_repasse_nao_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural, tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita Role Não Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
    )

@pytest.fixture
def receita_2020_1_ptrf_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_ptrf, tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        descricao="Receita PTRF Conferida",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
    )

@pytest.fixture
def receita_2019_2_role_repasse_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural, tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        descricao="Receita Role Conferida 2019",
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
    )
