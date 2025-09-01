import pytest
from model_bakery import baker


@pytest.fixture
def receita_prevista_pdde_resumo_recursos(resumo_recursos_paa, acao_pdde):
    return baker.make(
        'ReceitaPrevistaPdde',
        paa=resumo_recursos_paa,
        acao_pdde=acao_pdde,
        previsao_valor_custeio=1000.,
        previsao_valor_capital=1000.,
        previsao_valor_livre=1000.,
        saldo_custeio=1000.,
        saldo_capital=1000.,
        saldo_livre=1000.)
