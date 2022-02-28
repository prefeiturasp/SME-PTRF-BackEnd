import datetime

import pytest
from model_bakery import baker

from ...tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE


@pytest.fixture
def tipo_receita_repasse():
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True)


@pytest.fixture
def tipo_receita_rendimento():
    return baker.make('TipoReceita', nome='Rendimento', e_repasse=False)


@pytest.fixture
def receita_2020_1_role_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_role_repasse_custeio_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )


@pytest.fixture
def receita_2020_1_role_repasse_livre_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_LIVRE,
    )

@pytest.fixture
def receita_2020_1_role_repasse_capital_nao_conferida(associacao, conta_associacao_cartao,
                                                      acao_associacao_role_cultural,
                                                      tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_ptrf_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_ptrf,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2019_2_role_repasse_capital_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                  tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2019, 7, 10),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=True,
        categoria_receita=APLICACAO_CAPITAL,
    )


@pytest.fixture
def receita_2020_1_role_rendimento_custeio_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                     tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_rendimento,
        conferido=True,
        categoria_receita=APLICACAO_CUSTEIO,
    )

@pytest.fixture
def receita_2020_1_role_rendimento_livre_conferida(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                                     tipo_receita_rendimento):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_rendimento,
        conferido=True,
        categoria_receita=APLICACAO_LIVRE,
    )


@pytest.fixture
def tipo_receita_e_estorno():
    return baker.make('TipoReceita', nome='Estorno', e_estorno=True)


@pytest.fixture
def receita_estorno(tipo_receita_e_estorno, rateio_no_periodo_100_custeio):
    rateio = rateio_no_periodo_100_custeio
    return baker.make(
        'Receita',
        associacao=rateio.despesa.associacao,
        data=rateio.despesa.data_transacao,
        valor=rateio.valor_rateio,
        conta_associacao=rateio.conta_associacao,
        acao_associacao=rateio.acao_associacao,
        tipo_receita=tipo_receita_e_estorno,
        conferido=True,
        categoria_receita=rateio.aplicacao_recurso,
        rateio_estornado=rateio
    )
