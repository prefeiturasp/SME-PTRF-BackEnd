import pytest

from ....services import info_acao_associacao_no_periodo

pytestmark = pytest.mark.django_db

def test_resultado_periodo_fechado(
    fechamento_periodo,
):
    resultado_esperado = {
        'saldo_anterior_custeio': fechamento_periodo.saldo_anterior_custeio,
        'receitas_no_periodo_custeio': fechamento_periodo.total_receitas_custeio,
        'repasses_no_periodo_custeio': fechamento_periodo.total_repasses_custeio,
        'despesas_no_periodo_custeio': fechamento_periodo.total_despesas_custeio,
        'saldo_atual_custeio': fechamento_periodo.saldo_reprogramado_custeio,
        'despesas_nao_conciliadas_custeio': 16.0,
        'receitas_nao_conciliadas_custeio': 20.0,

        'receitas_devolucao_no_periodo_capital': fechamento_periodo.total_receitas_devolucao_capital,
        'receitas_devolucao_no_periodo_custeio': fechamento_periodo.total_receitas_devolucao_custeio,
        'receitas_devolucao_no_periodo_livre': fechamento_periodo.total_receitas_devolucao_livre,

        'saldo_anterior_capital': fechamento_periodo.saldo_anterior_capital,
        'receitas_no_periodo_capital': fechamento_periodo.total_receitas_capital,
        'repasses_no_periodo_capital': fechamento_periodo.total_repasses_capital,
        'despesas_no_periodo_capital': fechamento_periodo.total_despesas_capital,
        'saldo_atual_capital': fechamento_periodo.saldo_reprogramado_capital,
        'despesas_nao_conciliadas_capital': 8.0,
        'receitas_nao_conciliadas_capital': 10.0,

        'saldo_anterior_livre': fechamento_periodo.saldo_anterior_livre,
        'receitas_no_periodo_livre': fechamento_periodo.total_receitas_livre,
        'repasses_no_periodo_livre': fechamento_periodo.total_repasses_livre,
        'saldo_atual_livre': fechamento_periodo.saldo_reprogramado_livre,
        'receitas_nao_conciliadas_livre': 30.0,

    }
    resultado = info_acao_associacao_no_periodo(fechamento_periodo.acao_associacao, fechamento_periodo.periodo)

    assert resultado == resultado_esperado


def test_resultado_periodo_aberto_sem_receitas_sem_despesas(
    periodo,
    acao_associacao,
    fechamento_periodo_anterior
):
    resultado_esperado = {
        'saldo_anterior_custeio': 200,
        'receitas_no_periodo_custeio': 0,
        'repasses_no_periodo_custeio': 0,
        'despesas_no_periodo_custeio': 0,
        'saldo_atual_custeio': 200,
        'despesas_nao_conciliadas_custeio': 0.0,
        'receitas_nao_conciliadas_custeio': 0.0,

        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'saldo_anterior_capital': 100,
        'receitas_no_periodo_capital': 0,
        'repasses_no_periodo_capital': 0,
        'despesas_no_periodo_capital': 0,
        'saldo_atual_capital': 100,
        'despesas_nao_conciliadas_capital': 0.0,
        'receitas_nao_conciliadas_capital': 0.0,

        'saldo_anterior_livre': 2000,
        'receitas_no_periodo_livre': 0,
        'repasses_no_periodo_livre': 0,
        'saldo_atual_livre': 2000,
        'receitas_nao_conciliadas_livre': 0.0,

    }
    resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)

    assert resultado == resultado_esperado


def test_resultado_periodo_aberto_com_receitas_sem_despesas(
    periodo,
    acao_associacao,
    fechamento_periodo_anterior,
    receita_50_fora_do_periodo,
    receita_100_no_periodo,
    receita_200_no_inicio_do_periodo,
    receita_300_no_fim_do_periodo,
    receita_1000_no_periodo_livre_aplicacao
):
    resultado_esperado = {
        'saldo_anterior_custeio': 200,
        'receitas_no_periodo_custeio': 600,
        'repasses_no_periodo_custeio': 0,
        'despesas_no_periodo_custeio': 0,
        'saldo_atual_custeio': 800,
        'despesas_nao_conciliadas_custeio': 0.0,
        'receitas_nao_conciliadas_custeio': 600.0,

        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'saldo_anterior_capital': 100,
        'receitas_no_periodo_capital': 0,
        'repasses_no_periodo_capital': 0,
        'despesas_no_periodo_capital': 0,
        'saldo_atual_capital': 100,
        'despesas_nao_conciliadas_capital': 0.0,
        'receitas_nao_conciliadas_capital': 0.0,

        'saldo_anterior_livre': 2000,
        'receitas_no_periodo_livre': 1000,
        'repasses_no_periodo_livre': 0,
        'saldo_atual_livre': 3000,
        'receitas_nao_conciliadas_livre': 1000.0,

    }
    resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)

    assert resultado == resultado_esperado


def test_resultado_periodo_aberto_com_despesas_sem_receitas(
    periodo,
    acao_associacao,
    fechamento_periodo_anterior,
    despesa_no_periodo,
    rateio_no_periodo_10_custeio_outra_acao,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio
):
    resultado_esperado = {
        'saldo_anterior_custeio': 200,
        'receitas_no_periodo_custeio': 0,
        'repasses_no_periodo_custeio': 0,
        'despesas_no_periodo_custeio': 100,
        'saldo_atual_custeio': 100,
        'despesas_nao_conciliadas_custeio': 100.0,
        'receitas_nao_conciliadas_custeio': 0.0,

        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'saldo_anterior_capital': 100,
        'receitas_no_periodo_capital': 0,
        'repasses_no_periodo_capital': 0,
        'despesas_no_periodo_capital': 200,
        'saldo_atual_capital': -0,
        'despesas_nao_conciliadas_capital': 200.0,
        'receitas_nao_conciliadas_capital': 0.0,

        'saldo_anterior_livre': 2000,
        'receitas_no_periodo_livre': 0,
        'repasses_no_periodo_livre': 0,
        'saldo_atual_livre': 1900,
        'receitas_nao_conciliadas_livre': 0.0,

    }
    resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)

    assert resultado == resultado_esperado


def test_resultado_periodo_aberto_com_despesas_e_receitas(
    periodo,
    acao_associacao,
    fechamento_periodo_anterior,
    despesa_no_periodo,
    rateio_no_periodo_10_custeio_outra_acao,
    rateio_no_periodo_200_capital,
    rateio_no_periodo_100_custeio,
    despesa_fora_periodo,
    rateio_fora_periodo_50_custeio,
    receita_50_fora_do_periodo,
    receita_100_no_periodo,
    receita_200_no_inicio_do_periodo,
    receita_300_no_fim_do_periodo
):
    resultado_esperado = {
        'saldo_anterior_custeio': 200,
        'receitas_no_periodo_custeio': 600,
        'repasses_no_periodo_custeio': 0,
        'despesas_no_periodo_custeio': 100,
        'saldo_atual_custeio': 700,
        'despesas_nao_conciliadas_custeio': 100.0,
        'receitas_nao_conciliadas_custeio': 600.0,

        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'saldo_anterior_capital': 100,
        'receitas_no_periodo_capital': 0,
        'repasses_no_periodo_capital': 0,
        'despesas_no_periodo_capital': 200,
        'saldo_atual_capital': 0,
        'despesas_nao_conciliadas_capital': 200.0,
        'receitas_nao_conciliadas_capital': 0.0,

        'saldo_anterior_livre': 2000,
        'receitas_no_periodo_livre': 0,
        'repasses_no_periodo_livre': 0,
        'saldo_atual_livre': 1900,
        'receitas_nao_conciliadas_livre': 0.0,

    }
    resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)

    assert resultado == resultado_esperado


def test_resultado_periodo_aberto_consumo_do_saldo_livre_aplicacao(
    periodo,
    acao_associacao,
    fechamento_periodo_anterior_capital_1000_livre_2000,
    despesa_no_periodo,
    rateio_no_periodo_1500_capital,
    receita_100_no_periodo_capital
):
    resultado_esperado = {
        'saldo_anterior_custeio': 0,
        'receitas_no_periodo_custeio': 0,
        'repasses_no_periodo_custeio': 0,
        'despesas_no_periodo_custeio': 0,
        'saldo_atual_custeio': 0,
        'despesas_nao_conciliadas_custeio': 0.0,
        'receitas_nao_conciliadas_custeio': 0.0,

        'receitas_devolucao_no_periodo_capital': 0.0,
        'receitas_devolucao_no_periodo_custeio': 0.0,
        'receitas_devolucao_no_periodo_livre': 0.0,

        'saldo_anterior_capital': 1000,
        'receitas_no_periodo_capital': 100,
        'repasses_no_periodo_capital': 0,
        'despesas_no_periodo_capital': 1500,
        'saldo_atual_capital': 0,
        'despesas_nao_conciliadas_capital': 1500.0,
        'receitas_nao_conciliadas_capital': 100.0,

        'saldo_anterior_livre': 2000,
        'receitas_no_periodo_livre': 0,
        'repasses_no_periodo_livre': 0,
        'saldo_atual_livre': 1600,
        'receitas_nao_conciliadas_livre': 0.0,

    }
    resultado = info_acao_associacao_no_periodo(acao_associacao, periodo)

    assert resultado == resultado_esperado
