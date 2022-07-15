import pytest

from decimal import Decimal

from sme_ptrf_apps.core.services import ResumoRecursosService

pytestmark = pytest.mark.django_db


def test_retorna_saldo_posterior_zero_se_nao_houver_fechamentos_ou_movimentacao(
    rr_periodo_2019_1,
    rr_periodo_2019_2,
    rr_periodo_2020_1,
    rr_periodo_2020_2,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert resumo.saldo_posterior.total_geral == Decimal(0.00), "Deve retornar o saldo geral zerado."
    assert resumo.saldo_posterior.total_custeio == Decimal(0.00), "Deve retornar o saldo custeio zerado."
    assert resumo.saldo_posterior.total_capital == Decimal(0.00), "Deve retornar o saldo capital zerado."
    assert resumo.saldo_posterior.total_livre == Decimal(0.00), "Deve retornar o saldo livre zerado."


def test_retorna_saldo_posterior_de_fechamento_anterior_se_houver_e_nao_houver_movimentacao(
    rr_periodo_2019_1,
    rr_periodo_2019_2,
    rr_periodo_2020_1,
    rr_periodo_2020_2,
    rr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert resumo.saldo_posterior.total_geral == Decimal(770.00), "Deve retornar o saldo geral do fechamento 2019.1."
    assert resumo.saldo_posterior.total_custeio == Decimal(110.00), "Deve retornar o saldo custeio do fechamento 2019.1."
    assert resumo.saldo_posterior.total_capital == Decimal(110.00), "Deve retornar o saldo capital do fechamento 2019.1."
    assert resumo.saldo_posterior.total_livre == Decimal(550.00), "Deve retornar o saldo livre do fechamento 2019.1."


def test_retorna_saldo_posterior_conforme_movimentacao_se_nao_houver_fechamento_do_periodo(
    rr_periodo_2019_1,
    rr_periodo_2019_2,
    rr_periodo_2020_1,
    rr_periodo_2020_2,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_220_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_500_2020_1_role_cheque_custeio,  # Não soma pois é de outra ação.
    rr_receita_400_2020_1_ptrf_cartao_custeio,  # Não soma pois é de outra conta.
    rr_receita_650_2020_2_ptrf_cheque_custeio,  # Não soma pois é de outro período.
    rr_rateio_100_2020_1_ptrf_cheque_custeio,
    rr_rateio_200_2020_1_ptrf_cheque_capital,
    rr_rateio_400_2020_1_role_cheque_custeio,   # Não soma pois é de outra ação.
    rr_rateio_300_2020_1_ptrf_cartao_custeio,   # Não soma pois é de outra conta.
    rr_rateio_550_2020_2_ptrf_cheque_custeio,   # Não soma pois é de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert resumo.saldo_posterior.total_geral == Decimal(330.00), "Deve retornar o total de entradas - despesas."
    assert resumo.saldo_posterior.total_custeio == Decimal(10.00), "Deve retornar o total de entradas custeio - despesas custeio."
    assert resumo.saldo_posterior.total_capital == Decimal(20.00), "Deve retornar o total de entradas capital - despesas capital."
    assert resumo.saldo_posterior.total_livre == Decimal(300.00), "Deve retornar o total de entradas livre."


def test_retorna_saldo_posterior_conforme_movimentacao_de_periodo_sem_fechamento_mas_usando_saldo_de_fechamento_anterior(
    rr_periodo_2019_1,
    rr_periodo_2019_2,
    rr_periodo_2020_1,
    rr_periodo_2020_2,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_220_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_500_2020_1_role_cheque_custeio,  # Não soma pois é de outra ação.
    rr_receita_400_2020_1_ptrf_cartao_custeio,  # Não soma pois é de outra conta.
    rr_receita_650_2020_2_ptrf_cheque_custeio,  # Não soma pois é de outro período.
    rr_rateio_100_2020_1_ptrf_cheque_custeio,
    rr_rateio_200_2020_1_ptrf_cheque_capital,
    rr_rateio_400_2020_1_role_cheque_custeio,   # Não soma pois é de outra ação.
    rr_rateio_300_2020_1_ptrf_cartao_custeio,   # Não soma pois é de outra conta.
    rr_rateio_550_2020_2_ptrf_cheque_custeio,   # Não soma pois é de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert resumo.saldo_posterior.total_geral == Decimal(1100.00), "Deve retornar o total de entradas - despesas + saldo fechamento anterior."
    assert resumo.saldo_posterior.total_custeio == Decimal(120.00), "Deve retornar o total de entradas custeio - despesas custeio + saldo custeio do fechamento anterior."
    assert resumo.saldo_posterior.total_capital == Decimal(130.00), "Deve retornar o total de entradas capital - despesas capital + saldo capital do fechamento anterior."
    assert resumo.saldo_posterior.total_livre == Decimal(850.00), "Deve retornar o total de entradas livre + saldo livre do fechamento anterior."
