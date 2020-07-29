import pytest

from model_bakery import baker

from ....core.models import STATUS_FECHADO, STATUS_IMPLANTACAO

pytestmark = pytest.mark.django_db


@pytest.fixture
def fechamento_periodo_2019_2(periodo_2019_2, associacao, conta_associacao, acao_associacao, ):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2019_2,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=None,
        total_receitas_capital=3000,
        total_receitas_custeio=2000,
        total_receitas_livre=1000,
        status=STATUS_IMPLANTACAO
    )


@pytest.fixture
def fechamento_periodo_2020_1_saldos_positivos(periodo_2020_1, associacao, conta_associacao, acao_associacao,
                                               fechamento_periodo_2019_2):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_periodo_2019_2,
        total_receitas_capital=1000,
        total_despesas_capital=2000,
        total_receitas_custeio=2000,
        total_despesas_custeio=3000,
        total_receitas_livre=3000,
        status=STATUS_FECHADO,
    )


def test_calculo_saldo_reprogramado_saldos_positivos(fechamento_periodo_2020_1_saldos_positivos):
    fechamento = fechamento_periodo_2020_1_saldos_positivos
    assert fechamento.saldo_anterior == 6000, 'Erro no saldo anterior'
    assert fechamento.saldo_anterior_capital == 3000, 'Erro no saldo anterior (capital)'
    assert fechamento.saldo_anterior_custeio == 2000, 'Erro no saldo anterior (custeio)'
    assert fechamento.saldo_anterior_livre == 1000, 'Erro no saldo anterior (livre)'
    assert fechamento.saldo_reprogramado == 7000, 'Erro no saldo reprogramado'
    assert fechamento.saldo_reprogramado_capital == 2000, 'Erro no saldo reprogramado (capital)'
    assert fechamento.saldo_reprogramado_custeio == 1000, 'Erro no saldo reprogramado (custeio)'
    assert fechamento.saldo_reprogramado_livre == 4000, 'Erro no saldo reprogramado (livre)'


@pytest.fixture
def fechamento_periodo_2020_1_capital_negativo_com_saldo_livre(periodo_2020_1, associacao, conta_associacao,
                                                               acao_associacao,
                                                               fechamento_periodo_2019_2):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_periodo_2019_2,
        total_receitas_capital=0,
        total_despesas_capital=4000,
        total_receitas_custeio=0,
        total_despesas_custeio=0,
        total_receitas_livre=3000,
        status=STATUS_FECHADO,
    )


def test_calculo_saldo_reprogramado_capital_negativo_com_saldo_livres(
    fechamento_periodo_2020_1_capital_negativo_com_saldo_livre):
    fechamento = fechamento_periodo_2020_1_capital_negativo_com_saldo_livre
    assert fechamento.saldo_anterior == 6000, 'Erro no saldo anterior'
    assert fechamento.saldo_anterior_capital == 3000, 'Erro no saldo anterior (capital)'
    assert fechamento.saldo_anterior_custeio == 2000, 'Erro no saldo anterior (custeio)'
    assert fechamento.saldo_anterior_livre == 1000, 'Erro no saldo anterior (livre)'
    assert fechamento.saldo_reprogramado == 5000, 'Erro no saldo reprogramado'
    assert fechamento.saldo_reprogramado_capital == 0, 'Erro no saldo reprogramado (capital)'
    assert fechamento.saldo_reprogramado_custeio == 2000, 'Erro no saldo reprogramado (custeio)'
    assert fechamento.saldo_reprogramado_livre == 3000, 'Erro no saldo reprogramado (livre)'


@pytest.fixture
def fechamento_periodo_2020_1_custeio_negativo_com_saldo_livre(periodo_2020_1, associacao, conta_associacao,
                                                               acao_associacao,
                                                               fechamento_periodo_2019_2):
    return baker.make(
        'FechamentoPeriodo',
        periodo=periodo_2020_1,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        fechamento_anterior=fechamento_periodo_2019_2,
        total_receitas_capital=0,
        total_despesas_capital=0,
        total_receitas_custeio=0,
        total_despesas_custeio=3000,
        total_receitas_livre=3000,
        status=STATUS_FECHADO,
    )


def test_calculo_saldo_reprogramado_custeio_negativo_com_saldo_livres(
    fechamento_periodo_2020_1_custeio_negativo_com_saldo_livre):
    fechamento = fechamento_periodo_2020_1_custeio_negativo_com_saldo_livre
    assert fechamento.saldo_anterior == 6000, 'Erro no saldo anterior'
    assert fechamento.saldo_anterior_capital == 3000, 'Erro no saldo anterior (capital)'
    assert fechamento.saldo_anterior_custeio == 2000, 'Erro no saldo anterior (custeio)'
    assert fechamento.saldo_anterior_livre == 1000, 'Erro no saldo anterior (livre)'
    assert fechamento.saldo_reprogramado == 6000, 'Erro no saldo reprogramado'
    assert fechamento.saldo_reprogramado_capital == 3000, 'Erro no saldo reprogramado (capital)'
    assert fechamento.saldo_reprogramado_custeio == 0, 'Erro no saldo reprogramado (custeio)'
    assert fechamento.saldo_reprogramado_livre == 3000, 'Erro no saldo reprogramado (livre)'
