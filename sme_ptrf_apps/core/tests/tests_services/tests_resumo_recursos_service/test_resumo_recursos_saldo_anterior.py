import pytest

from decimal import Decimal

from sme_ptrf_apps.core.services import ResumoRecursosService

pytestmark = pytest.mark.django_db


def test_se_existe_fechamento_do_periodo_anterior_para_a_acao_e_conta_deve_retornar_o_saldo_do_fechamento(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,  # Esse deve ser considerado como saldo anterior do 2019.2
    rr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
    rr_fechamento_400_2019_2_ptrf_cartao_rcp500_dcp300_rct200_dct100_rlv100,  # Não deve ser somado por ser de outra conta.
    rr_fechamento_900_2019_2_role_cheque_rcp300_dcp100_rct500_dct200_rlv400,  # Não deve ser somado por ser de outra ação.
    rr_fechamento_2600_2020_2_ptrf_cheque_rcp230_dcp120_rct450_dct340_rlv560,  # Não deve ser somado por ser de um período posterior e não anterior.
    rr_fechamento_1820_2020_1_ptrf_cheque_rcp200_dcp200_rct100_dct100_rlv300,  # Não deve ser somado por ser do próprio período e não anterior.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert resumo.saldo_anterior.total_geral == Decimal(1520.00), "Deve retornar o saldo geral do fechamento 2019.2 PTRF Cheque."
    assert resumo.saldo_anterior.total_custeio == Decimal(210.00), "Deve retornar o saldo custeio do fechamento 2019.2 PTRF Cheque."
    assert resumo.saldo_anterior.total_capital == Decimal(260.00), "Deve retornar o saldo capital do fechamento 2019.2 PTRF Cheque."
    assert resumo.saldo_anterior.total_livre == Decimal(1050.00), "Deve retornar o saldo livre do fechamento 2019.2 PTRF Cheque."


def test_se_existe_fechamento_do_periodo_imediatamente_anterior_para_a_acao_qualquer_conta_deve_retornar_o_saldo_somado_dos_fechamentos(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,  # Esse deve ser considerado como saldo anterior do 2019.2
    rr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
    rr_fechamento_400_2019_2_ptrf_cartao_rcp500_dcp300_rct200_dct100_rlv100,
    rr_fechamento_900_2019_2_role_cheque_rcp300_dcp100_rct500_dct200_rlv400,  # Não deve ser somado por ser de outra ação.
    rr_fechamento_2600_2020_2_ptrf_cheque_rcp230_dcp120_rct450_dct340_rlv560,  # Não deve ser somado por ser de um período posterior e não anterior.
    rr_fechamento_1820_2020_1_ptrf_cheque_rcp200_dcp200_rct100_dct100_rlv300,  # Não deve ser somado por ser do próprio período e não anterior.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.saldo_anterior.total_geral == Decimal(1520.00), "Deve retornar o saldo geral somado dos fechamentos 2019.2 PTRF."
    assert resumo.saldo_anterior.total_custeio == Decimal(210.00), "Deve retornar o saldo custeio somado dos fechamentos 2019.2 PTRF."
    assert resumo.saldo_anterior.total_capital == Decimal(260.00), "Deve retornar o saldo capital somado dos fechamentos 2019.2 PTRF."
    assert resumo.saldo_anterior.total_livre == Decimal(1050.00), "Deve retornar o saldo livre somado dos fechamentos 2019.2 PTRF."


def test_se_existe_fechamento_do_periodo_nao_imediatamente_anterior_para_a_acao_qualquer_conta_deve_retornar_o_saldo_somado_dos_fechamentos(
    rr_periodo_2019_2,
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.saldo_anterior.total_geral == Decimal(770.00), "Deve retornar o saldo geral do fechamento 2019.1 PTRF."
    assert resumo.saldo_anterior.total_custeio == Decimal(110.00), "Deve retornar o saldo custeio do fechamento 2019.1 PTRF."
    assert resumo.saldo_anterior.total_capital == Decimal(110.00), "Deve retornar o saldo capital do fechamento 2019.1 PTRF."
    assert resumo.saldo_anterior.total_livre == Decimal(550.00), "Deve retornar o saldo livre do fechamento 2019.1 PTRF."
