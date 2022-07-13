import pytest

from decimal import Decimal

from sme_ptrf_apps.core.services import ResumoRecursosService

pytestmark = pytest.mark.django_db


def test_resumo_de_recursos_deve_somar_apenas_as_despesas_do_periodo_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_rateio_100_2020_1_ptrf_cheque_custeio,
    rr_rateio_200_2020_1_ptrf_cheque_capital,
    rr_rateio_300_2020_1_ptrf_cartao_custeio,    # Essa não deve ser somado por ser de outra conta.
    rr_rateio_400_2020_1_role_cheque_custeio,    # Essa não deve ser somado por ser de outra ação.
    rr_rateio_550_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somado por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque,
    )

    assert resumo.despesas.total_geral == 300.00, "Deve somar apenas os rateios do período, ação e conta definidos."


def test_resumo_de_recursos_deve_somar_as_despesas_do_periodo_por_categoria_para_determinada_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_rateio_100_2020_1_ptrf_cheque_custeio,
    rr_rateio_200_2020_1_ptrf_cheque_capital,
    rr_rateio_300_2020_1_ptrf_cartao_custeio,    # Essa não deve ser somado por ser de outra conta.
    rr_rateio_400_2020_1_role_cheque_custeio,    # Essa não deve ser somado por ser de outra ação.
    rr_rateio_550_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somado por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque,
    )

    assert resumo.despesas.total_custeio == Decimal(100.00), "Deve somar apenas os rateios do tipo custeio."
    assert resumo.despesas.total_capital == Decimal(200.00), "Deve somar apenas os rateios do tipo capital."
    assert (
               resumo.despesas.total_custeio +
               resumo.despesas.total_capital ==
               resumo.despesas.total_geral
    ), "O somatório dos totais por categoria deve ser igual ao total geral."


def test_resumo_de_recursos_deve_somar_as_despesas_do_periodo_por_categoria_para_determinada_acao_e_todas_as_contas_se_conta_nao_for_definida(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_rateio_100_2020_1_ptrf_cheque_custeio,
    rr_rateio_200_2020_1_ptrf_cheque_capital,
    rr_rateio_300_2020_1_ptrf_cartao_custeio,
    rr_rateio_400_2020_1_role_cheque_custeio,    # Essa não deve ser somado por ser de outra ação.
    rr_rateio_550_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somado por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.despesas.total_custeio == Decimal(400.00), "Deve somar apenas os rateios do tipo custeio em todas as contas."
    assert resumo.despesas.total_capital == Decimal(200.00), "Deve somar apenas os rateios do tipo capital em todas as contas."
    assert (
               resumo.despesas.total_custeio +
               resumo.despesas.total_capital ==
               resumo.despesas.total_geral
    ), "O somatório dos totais por categoria deve ser igual ao total geral."
