import pytest

from decimal import Decimal
from freezegun import freeze_time

from sme_ptrf_apps.core.services.painel_resumo_recursos_service import (
    PainelResumoRecursosService,
    PainelResumoRecursosCardConta,
)

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-01 10:20:00')
def test_painel_resumo_recursos_retorna_info_conta(
    prr_associacao,
    prr_periodo_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    prr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
    prr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
    prr_fechamento_900_2019_2_role_cheque_rcp300_dcp100_rct500_dct200_rlv400,
    prr_fechamento_400_2019_2_ptrf_cartao_rcp500_dcp300_rct200_dct100_rlv100,  # Não entra por ser de outra conta
    prr_receita_110_2020_1_ptrf_cheque_custeio,
    prr_receita_110_2020_1_ptrf_cheque_custeio_repasse,
    prr_receita_220_2020_1_ptrf_cheque_capital,
    prr_receita_300_2020_1_ptrf_cheque_livre,
    prr_receita_500_2020_1_role_cheque_custeio,
    prr_receita_400_2020_1_ptrf_cartao_custeio,  # Não entra por ser de outra conta
    prr_rateio_100_2020_1_ptrf_cheque_custeio,
    prr_rateio_200_2020_1_ptrf_cheque_capital,
    prr_rateio_400_2020_1_role_cheque_custeio,
    prr_rateio_300_2020_1_ptrf_cartao_custeio,   # Não entra por ser de outra conta

):
    painel = PainelResumoRecursosService.painel_resumo_recursos(
        prr_associacao,
        prr_periodo_2020_1,
        prr_conta_associacao_cheque
    )

    info_conta = painel.info_conta

    assert isinstance(info_conta, PainelResumoRecursosCardConta), "info_conta devem ser do tipo correto."

    assert info_conta.conta_associacao_uuid == prr_conta_associacao_cheque.uuid
    assert info_conta.conta_associacao_nome == prr_conta_associacao_cheque.tipo_conta.nome

    assert info_conta.saldo_reprogramado == Decimal(2420.00)
    assert info_conta.saldo_reprogramado_capital == Decimal(460.00)
    assert info_conta.saldo_reprogramado_custeio == Decimal(510.00)
    assert info_conta.saldo_reprogramado_livre == Decimal(1450.00)

    assert info_conta.receitas_no_periodo == Decimal(1240.00)

    assert info_conta.repasses_no_periodo == Decimal(110.00)
    assert info_conta.repasses_no_periodo_capital == Decimal(0.00)
    assert info_conta.repasses_no_periodo_custeio == Decimal(110.00)
    assert info_conta.repasses_no_periodo_livre == Decimal(0.00)

    assert info_conta.outras_receitas_no_periodo == Decimal(1130.00)
    assert info_conta.outras_receitas_no_periodo_capital == Decimal(220.00)
    assert info_conta.outras_receitas_no_periodo_custeio == Decimal(610.00)
    assert info_conta.outras_receitas_no_periodo_livre == Decimal(300.00)

    assert info_conta.despesas_no_periodo == Decimal(700.00)
    assert info_conta.despesas_no_periodo_capital == Decimal(200.00)
    assert info_conta.despesas_no_periodo_custeio == Decimal(500.00)

    assert info_conta.saldo_atual_total == Decimal(2960.00)
    assert info_conta.saldo_atual_capital == Decimal(480.00)
    assert info_conta.saldo_atual_custeio == Decimal(730.00)
    assert info_conta.saldo_atual_livre == Decimal(1750.00)

