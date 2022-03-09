import pytest
from datetime import date
from model_bakery import baker

from sme_ptrf_apps.core.models.fechamento_periodo import STATUS_IMPLANTACAO, STATUS_FECHADO

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo_implantacao_2019_1():
    return baker.make(
        'Periodo',
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 6, 30),
        periodo_anterior=None
    )


@pytest.fixture
def periodo_fechamento_2019_2(periodo_implantacao_2019_1):
    return baker.make(
        'Periodo',
        referencia='2019.2',
        data_inicio_realizacao_despesas=date(2019, 7, 1),
        data_fim_realizacao_despesas=date(2019, 12, 31),
        periodo_anterior=periodo_implantacao_2019_1
    )


@pytest.fixture
def periodo_fechamento_2020_1(periodo_fechamento_2019_2):
    return baker.make(
        'Periodo',
        referencia='2020.1',
        data_inicio_realizacao_despesas=date(2020, 1, 1),
        data_fim_realizacao_despesas=date(2020, 6, 30),
        periodo_anterior=periodo_fechamento_2019_2
    )


@pytest.fixture
def fechamento_implantacao_2019_1(periodo_implantacao_2019_1, associacao, conta_associacao, acao_associacao):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_implantacao_2019_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        status=STATUS_IMPLANTACAO,
    )


@pytest.fixture
def prestacao_conta_2019_2(periodo_fechamento_2019_2, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1000,
        periodo=periodo_fechamento_2019_2,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def fechamento_2019_2(
    periodo_fechamento_2019_2,
    associacao,
    conta_associacao,
    acao_associacao,
    fechamento_implantacao_2019_1,
    prestacao_conta_2019_2
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_fechamento_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_implantacao_2019_1,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2019_2
    )


@pytest.fixture
def prestacao_conta_2020_1_em_analise(periodo_fechamento_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1001,
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        status="EM_ANALISE"
    )


@pytest.fixture
def fechamento_2020_1(
    periodo_fechamento_2020_1,
    associacao,
    conta_associacao,
    acao_associacao,
    fechamento_2019_2,
    prestacao_conta_2020_1_em_analise
):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_2019_2,
        status=STATUS_FECHADO,
        prestacao_conta=prestacao_conta_2020_1_em_analise
    )


@pytest.fixture
def prestacao_conta_2020_1_devolvida(periodo_fechamento_2020_1, associacao):
    return baker.make(
        'PrestacaoConta',
        id=1002,
        periodo=periodo_fechamento_2020_1,
        associacao=associacao,
        status="DEVOLVIDA"
    )


def test_nao_pode_reabrir_se_houver_fechamentos_posteriores(
    prestacao_conta_2020_1_em_analise,
    fechamento_2020_1,
    prestacao_conta_2019_2,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
):
    assert not prestacao_conta_2019_2.pode_reabrir()


def test_pode_reabrir_se_nao_houver_fechamentos_posteriores(
    prestacao_conta_2019_2,
    fechamento_2019_2,
    fechamento_implantacao_2019_1,
):
    assert prestacao_conta_2019_2.pode_reabrir()


def test_pode_reabrir_quando_proxima_pc_esta_devolvida(
    prestacao_conta_2020_1_devolvida,
    prestacao_conta_2019_2,
    fechamento_implantacao_2019_1,
    fechamento_2019_2
):
    assert prestacao_conta_2019_2.pode_reabrir()
