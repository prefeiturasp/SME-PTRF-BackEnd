import pytest

from decimal import Decimal

from sme_ptrf_apps.core.services import ResumoRecursosService

pytestmark = pytest.mark.django_db


def test_resumo_de_recursos_deve_somar_apenas_as_receitas_do_periodo_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_220_2020_1_ptrf_cheque_capital,
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

    assert resumo.receitas.total_geral == 630.00, "Deve somar apenas as receitas do período, ação e conta definidos."


def test_resumo_de_recursos_deve_somar_as_receitas_do_periodo_por_categoria_para_determinada_acao_e_conta(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_220_2020_1_ptrf_cheque_capital,
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

    assert resumo.receitas.total_custeio == Decimal(110.00), "Deve somar apenas as receitas do tipo custeio."
    assert resumo.receitas.total_capital == Decimal(220.00), "Deve somar apenas as receitas do tipo capital."
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
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_220_2020_1_ptrf_cheque_capital,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_400_2020_1_ptrf_cartao_custeio,
    rr_receita_500_2020_1_role_cheque_custeio,    # Essa não deve ser somada por ser de outra ação.
    rr_receita_650_2020_2_ptrf_cheque_custeio,    # Essa não deve ser somada por ser de outro período.
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.receitas.total_custeio == Decimal(510.00), "Deve somar apenas as receitas do tipo custeio em todas as contas."
    assert resumo.receitas.total_capital == Decimal(220.00), "Deve somar apenas as receitas do tipo capital em todas as contas."
    assert resumo.receitas.total_livre == Decimal(300.00), "Deve somar apenas as receitas do tipo livre em todas as contas."
    assert resumo.receitas.total_geral == Decimal(1030.00), "O somatório dos totais por categoria deve ser igual ao total geral."


def test_resumo_de_recursos_deve_usar_somatorio_de_receitas_dos_fechamentos_do_periodo_se_existirem(
    rr_periodo_2019_2,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
    rr_fechamento_400_2019_2_ptrf_cartao_rcp500_dcp300_rct200_dct100_rlv100,
    rr_fechamento_900_2019_2_role_cheque_rcp300_dcp100_rct500_dct200_rlv400,  # Esse não entra por ser de outra ação
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2019_2,
        rr_acao_associacao_ptrf,
    )

    assert resumo.receitas.total_custeio == Decimal(600.00), "Deve somar apenas as receitas do tipo custeio dos fechamentos de todas as contas."
    assert resumo.receitas.total_capital == Decimal(750.00), "Deve somar apenas as receitas do tipo capital em todas as contas."
    assert resumo.receitas.total_livre == Decimal(600.00), "Deve somar apenas as receitas do tipo livre em todas as contas."
    assert resumo.receitas.total_geral == Decimal(1950.00), "O somatório dos totais por categoria deve ser igual ao total geral."


def test_resumo_de_recursos_deve_somar_as_receitas_do_periodo_por_categoria_separando_repasse_e_outras_receitas(
    rr_periodo_2020_1,
    rr_acao_associacao_ptrf,
    rr_conta_associacao_cheque,
    rr_receita_110_2020_1_ptrf_cheque_custeio,
    rr_receita_110_2020_1_ptrf_cheque_custeio_repasse,
    rr_receita_220_2020_1_ptrf_cheque_capital,
    rr_receita_220_2020_1_ptrf_cheque_capital_repasse,
    rr_receita_300_2020_1_ptrf_cheque_livre,
    rr_receita_300_2020_1_ptrf_cheque_livre_repasse,
    rr_receita_400_2020_1_ptrf_cartao_custeio,
):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
    )

    assert resumo.receitas.outras_custeio == Decimal(510.00), "Deve somar apenas as receitas do tipo custeio que não são repasses."
    assert resumo.receitas.outras_capital == Decimal(220.00), "Deve somar apenas as receitas do tipo capital que não são repasses."
    assert resumo.receitas.outras_livre == Decimal(300.00), "Deve somar apenas as receitas do tipo livre que não são repasses."
    assert resumo.receitas.outras_geral == Decimal(1030.00), "Deve ser o total das receitas que não são repasses."

    assert resumo.receitas.repasses_custeio == Decimal(110.00), "Deve somar apenas as receitas do tipo custeio que são repasses."
    assert resumo.receitas.repasses_capital == Decimal(220.00), "Deve somar apenas as receitas do tipo capital que são repasses."
    assert resumo.receitas.repasses_livre == Decimal(300.00), "Deve somar apenas as receitas do tipo livre que são repasses."
    assert resumo.receitas.repasses_geral == Decimal(630.00), "Deve ser o total das receitas que são repasses."


