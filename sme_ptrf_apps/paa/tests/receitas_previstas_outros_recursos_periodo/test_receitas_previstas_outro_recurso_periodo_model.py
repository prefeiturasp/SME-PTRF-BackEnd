import pytest
from sme_ptrf_apps.paa.models import ReceitaPrevistaOutroRecursoPeriodo
from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaOutroRecursoPeriodoFactory


@pytest.mark.django_db
def test_create_receita_prevista_outro_recurso_periodo(paa, outro_recurso_periodo):
    receita = ReceitaPrevistaOutroRecursoPeriodoFactory(
        paa=paa,
        outro_recurso_periodo=outro_recurso_periodo,
        previsao_valor_custeio=1000.0,
        previsao_valor_capital=1010.0,
        previsao_valor_livre=1020.0,
        saldo_custeio=1030.0,
        saldo_capital=1040.0,
        saldo_livre=1050.0
    )

    assert ReceitaPrevistaOutroRecursoPeriodo.objects.count() == 1
    assert receita.outro_recurso_periodo == outro_recurso_periodo
    assert receita.previsao_valor_custeio == 1000.0
    assert receita.previsao_valor_capital == 1010.0
    assert receita.previsao_valor_livre == 1020.0
    assert receita.saldo_custeio == 1030.0
    assert receita.saldo_capital == 1040.0
    assert receita.saldo_livre == 1050.0
