import pytest
from sme_ptrf_apps.paa.models import ReceitaPrevistaPaa
from sme_ptrf_apps.paa.fixtures.factories import ReceitaPrevistaPaaFactory


@pytest.mark.django_db
def test_create_receita_prevista_paa(paa, acao_associacao):
    receita = ReceitaPrevistaPaaFactory(
        paa=paa,
        acao_associacao=acao_associacao,
        previsao_valor_custeio=1000.0,
        previsao_valor_capital=1010.0,
        previsao_valor_livre=1020.0
    )

    assert ReceitaPrevistaPaa.objects.count() == 1
    assert receita.acao_associacao == acao_associacao
    assert receita.previsao_valor_custeio == 1000.0
    assert receita.previsao_valor_capital == 1010.0
    assert receita.previsao_valor_livre == 1020.0
