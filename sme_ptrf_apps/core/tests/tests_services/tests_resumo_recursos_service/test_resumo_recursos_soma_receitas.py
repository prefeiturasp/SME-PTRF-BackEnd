import pytest

from decimal import Decimal

from sme_ptrf_apps.core.services import ResumoRecursosService

pytestmark = pytest.mark.django_db


def test_resumo_de_recursos_deve_somar_apenas_as_receitas_do_periodo_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_100_2020_1_ptrf_cheque_custeio,
    rr_receita_200_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_400_2020_1_ptrf_cartao_custeio,    # Essa não deve ser somada por ser de outra conta.
    rr_receita_500_2020_1_role_cheque_custeio,    # Essa não deve ser somada por ser de outra ação.
    rr_receita_650_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somada por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque,
    )

    assert resumo.receitas.total_geral == 600.00, "Deve somar apenas as receitas do período, ação e conta definidos."


def test_resumo_de_recursos_deve_somar_as_receitas_do_periodo_por_categoria_para_determinada_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_100_2020_1_ptrf_cheque_custeio,
    rr_receita_200_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_400_2020_1_ptrf_cartao_custeio,    # Essa não deve ser somada por ser de outra conta.
    rr_receita_500_2020_1_role_cheque_custeio,    # Essa não deve ser somada por ser de outra ação.
    rr_receita_650_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somada por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque,
    )

    assert resumo.receitas.total_custeio == Decimal(100.00), "Deve somar apenas as receitas do tipo custeio."
    assert resumo.receitas.total_capital == Decimal(200.00), "Deve somar apenas as receitas do tipo capital."
    assert resumo.receitas.total_livre == Decimal(300.00), "Deve somar apenas as receitas do tipo livre."
    assert (
               resumo.receitas.total_custeio +
               resumo.receitas.total_capital +
               resumo.receitas.total_livre ==
               resumo.receitas.total_geral
    ), "O somatório dos totais por categoria deve ser igual ao total geral."


def test_resumo_de_recursos_deve_somar_as_receitas_do_periodo_por_categoria_para_determinada_acao_e_todas_as_contas_se_conta_nao_for_definida(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_100_2020_1_ptrf_cheque_custeio,
    rr_receita_200_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_400_2020_1_ptrf_cartao_custeio,
    rr_receita_500_2020_1_role_cheque_custeio,    # Essa não deve ser somada por ser de outra ação.
    rr_receita_650_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somada por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.receitas.total_custeio == Decimal(500.00), "Deve somar apenas as receitas do tipo custeio em todas as contas."
    assert resumo.receitas.total_capital == Decimal(200.00), "Deve somar apenas as receitas do tipo capital em todas as contas."
    assert resumo.receitas.total_livre == Decimal(300.00), "Deve somar apenas as receitas do tipo livre em todas as contas."
    assert (
               resumo.receitas.total_custeio +
               resumo.receitas.total_capital +
               resumo.receitas.total_livre ==
               resumo.receitas.total_geral
    ), "O somatório dos totais por categoria deve ser igual ao total geral."
