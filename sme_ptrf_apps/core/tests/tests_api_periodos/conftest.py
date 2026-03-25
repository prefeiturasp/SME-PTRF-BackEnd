import pytest

from datetime import date

UUID_DRE_TESTE = '93759585-8a8b-4c8e-9b1a-9f0c5d2e6b1a'
UUID_RECURSO_A = '923c9c89-cba9-48f1-8b86-97ae97946356'

@pytest.fixture
def periodo_2020_4(periodo_factory):
    return periodo_factory(
        referencia='2020.4',
        data_inicio_realizacao_despesas=date(2020, 10, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=date(2020, 10, 1),
        data_inicio_prestacao_contas=date(2021, 1, 1),
        data_fim_prestacao_contas=date(2021, 1, 15),
        periodo_anterior=None,
    )


@pytest.fixture
def periodo_2021_1(periodo_factory, periodo_2020_4):
    return periodo_factory(
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 3, 31),
        data_prevista_repasse=date(2021, 1, 1),
        data_inicio_prestacao_contas=date(2021, 4, 1),
        data_fim_prestacao_contas=date(2021, 4, 15),
        periodo_anterior=periodo_2020_4,
    )


@pytest.fixture
def periodo_2021_2(periodo_factory, periodo_2021_1):
    return periodo_factory(
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=periodo_2021_1,
    )


@pytest.fixture
def periodo_2021_2_aberto(periodo_factory, periodo_2021_1):
    return periodo_factory(
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=None,
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=periodo_2021_1,
    )

@pytest.fixture
def recurso_a(recurso_factory):
    return recurso_factory.create(uuid=UUID_RECURSO_A, nome='Recurso A', ativo=True)

@pytest.fixture
def periodo_2020_4_com_recurso_a(periodo_factory, recurso_a):
    return periodo_factory(
        referencia='2020.4',
        data_inicio_realizacao_despesas=date(2020, 10, 1),
        data_fim_realizacao_despesas=date(2020, 12, 31),
        data_prevista_repasse=date(2020, 10, 1),
        data_inicio_prestacao_contas=date(2021, 1, 1),
        data_fim_prestacao_contas=date(2021, 1, 15),
        periodo_anterior=None,
        recurso=recurso_a
    )

@pytest.fixture
def periodo_2021_1_com_recurso_a(periodo_factory, periodo_2020_4_com_recurso_a):
    recurso_a = periodo_2020_4_com_recurso_a.recurso

    return periodo_factory(
        referencia='2021.1',
        data_inicio_realizacao_despesas=date(2021, 1, 1),
        data_fim_realizacao_despesas=date(2021, 3, 31),
        data_prevista_repasse=date(2021, 1, 1),
        data_inicio_prestacao_contas=date(2021, 4, 1),
        data_fim_prestacao_contas=date(2021, 4, 15),
        periodo_anterior=periodo_2020_4_com_recurso_a,
        recurso=recurso_a
    )


@pytest.fixture
def periodo_2021_2_com_recurso_legado_ptrf(periodo_factory):
    return periodo_factory(
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 4, 1),
        data_fim_realizacao_despesas=date(2021, 6, 30),
        data_prevista_repasse=date(2021, 4, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=None
    )

@pytest.fixture
def periodo_2021_3_com_recurso_legado_ptrf(periodo_factory, periodo_2021_2_com_recurso_legado_ptrf):
    return periodo_factory(
        referencia='2021.3',
        data_inicio_realizacao_despesas=date(2021, 7, 1),
        data_fim_realizacao_despesas=date(2021, 9, 30),
        data_prevista_repasse=date(2021, 7, 1),
        data_inicio_prestacao_contas=date(2021, 7, 1),
        data_fim_prestacao_contas=date(2021, 7, 15),
        periodo_anterior=periodo_2021_2_com_recurso_legado_ptrf
    )

@pytest.fixture
def unidade_dre_teste(dre_factory):
    return dre_factory.create(uuid=UUID_DRE_TESTE, nome="DRE Teste")

@pytest.fixture
def unidade_ue_teste(unidade_factory, unidade_dre_teste):
    return unidade_factory.create(dre=unidade_dre_teste, tipo_unidade='UE', nome="UE Teste")

@pytest.fixture
def associacao_periodo_inicial_teste(associacao_factory, unidade_ue_teste, periodo_2021_2_com_recurso_legado_ptrf):
    return associacao_factory.create(
        unidade=unidade_ue_teste,
        nome="UE Teste",
        periodo_inicial=periodo_2021_2_com_recurso_legado_ptrf
    )

@pytest.fixture
def periodo_inicial_associacao_teste(periodo_inicial_associacao_factory, periodo_2020_4_com_recurso_a, associacao_periodo_inicial_teste):
    return periodo_inicial_associacao_factory(
        periodo_inicial=periodo_2020_4_com_recurso_a,
        associacao=associacao_periodo_inicial_teste,
        recurso=periodo_2020_4_com_recurso_a.recurso
    )
