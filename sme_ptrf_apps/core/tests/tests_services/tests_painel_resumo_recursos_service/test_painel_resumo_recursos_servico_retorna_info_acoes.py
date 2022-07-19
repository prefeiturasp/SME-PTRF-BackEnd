import pytest

from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time

from sme_ptrf_apps.core.services.painel_resumo_recursos_service import (
    PainelResumoRecursosService,
    PainelResumoRecursos,
    PainelResumoRecursosCardConta,
    PainelResumoRecursosCardAcao
)

pytestmark = pytest.mark.django_db


@freeze_time('2020-01-01 10:20:00')
def test_painel_resumo_recursos_retorna_info_acoes(
    prr_associacao,
    prr_periodo_2020_1,
    prr_conta_associacao_cheque,
    prr_acao_associacao_ptrf,
    prr_fechamento_770_2019_1_ptrf_cheque_rcp220_dcp110_rct440_dct330_rlv550,
    prr_fechamento_1520_2019_2_ptrf_cheque_rcp250_dcp100_rct400_dct300_rlv500,
    prr_receita_110_2020_1_ptrf_cheque_custeio,
    prr_receita_110_2020_1_ptrf_cheque_custeio_repasse,
    prr_receita_220_2020_1_ptrf_cheque_capital,
    prr_receita_300_2020_1_ptrf_cheque_livre,
    prr_rateio_100_2020_1_ptrf_cheque_custeio,
    prr_rateio_200_2020_1_ptrf_cheque_capital,
):
    painel = PainelResumoRecursosService.painel_resumo_recursos(
        prr_associacao,
        prr_periodo_2020_1,
        prr_conta_associacao_cheque
    )

    assert len(painel.info_acoes) == 1, "Deve retornar informações de uma ação"

    info_acao = painel.info_acoes[0]

    assert isinstance(info_acao, PainelResumoRecursosCardAcao), "info_acoes devem ser do tipo correto."

    assert info_acao.acao_associacao_uuid == prr_acao_associacao_ptrf.uuid
    assert info_acao.acao_associacao_nome == prr_acao_associacao_ptrf.acao.nome

    assert info_acao.saldo_reprogramado == Decimal(1520.00)
    assert info_acao.saldo_reprogramado_capital == Decimal(260.00)
    assert info_acao.saldo_reprogramado_custeio == Decimal(210.00)
    assert info_acao.saldo_reprogramado_livre == Decimal(1050.00)

    assert info_acao.receitas_no_periodo == Decimal(740.00)

    assert info_acao.repasses_no_periodo == Decimal(110.00)
    assert info_acao.repasses_no_periodo_capital == Decimal(0.00)
    assert info_acao.repasses_no_periodo_custeio == Decimal(110.00)
    assert info_acao.repasses_no_periodo_livre == Decimal(0.00)

    assert info_acao.outras_receitas_no_periodo == Decimal(630.00)
    assert info_acao.outras_receitas_no_periodo_capital == Decimal(220.00)
    assert info_acao.outras_receitas_no_periodo_custeio == Decimal(110.00)
    assert info_acao.outras_receitas_no_periodo_livre == Decimal(300.00)

    assert info_acao.despesas_no_periodo == Decimal(300.00)
    assert info_acao.despesas_no_periodo_capital == Decimal(200.00)
    assert info_acao.despesas_no_periodo_custeio == Decimal(100.00)

    assert info_acao.saldo_atual_total == Decimal(1960.00)
    assert info_acao.saldo_atual_capital == Decimal(280.00)
    assert info_acao.saldo_atual_custeio == Decimal(330.00)
    assert info_acao.saldo_atual_livre == Decimal(1350.00)
