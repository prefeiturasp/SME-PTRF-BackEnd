import pytest

from sme_ptrf_apps.core.services.resumo_rescursos_service import (
    ResumoRecursosService,
    ResumoRecursos,
    ResumoReceitas,
    ResumoDespesas,
    ResumoSaldo,
)

pytestmark = pytest.mark.django_db


def test_obtem_resumo_por_conta_e_acao(rr_periodo_2020_1, rr_acao_associacao_ptrf, rr_conta_associacao_cheque):
    resumo = ResumoRecursosService.resumo_recursos(
        rr_periodo_2020_1,
        rr_acao_associacao_ptrf,
        rr_conta_associacao_cheque
    )

    assert isinstance(resumo, ResumoRecursos)
    assert resumo.periodo == rr_periodo_2020_1
    assert resumo.acao_associacao == rr_acao_associacao_ptrf
    assert resumo.conta_associacao == rr_conta_associacao_cheque
    assert isinstance(resumo.saldo_anterior, ResumoSaldo)
    assert isinstance(resumo.receitas, ResumoReceitas)
    assert isinstance(resumo.despesas, ResumoDespesas)
    assert isinstance(resumo.saldo_posterior, ResumoSaldo)
