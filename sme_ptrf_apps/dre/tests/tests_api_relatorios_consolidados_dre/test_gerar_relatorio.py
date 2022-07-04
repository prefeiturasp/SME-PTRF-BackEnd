import pytest
from model_bakery import baker
from ...models import RelatorioConsolidadoDRE
from ...services import gera_relatorio_dre

pytestmark = pytest.mark.django_db


@pytest.fixture
def ano_analise_regularidade_2019():
    return baker.make('AnoAnaliseRegularidade', ano=2019)


def test_gerar_relatorio_final(periodo, dre, tipo_conta, ano_analise_regularidade_2019):
    gera_relatorio_dre(dre, periodo, tipo_conta)

    assert RelatorioConsolidadoDRE.objects.exists()
    assert RelatorioConsolidadoDRE.objects.first().status == RelatorioConsolidadoDRE.STATUS_GERADO_TOTAL


def test_gerar_relatorio_parcial(periodo, dre, tipo_conta, ano_analise_regularidade_2019):
    gera_relatorio_dre(dre, periodo, tipo_conta, True)

    assert RelatorioConsolidadoDRE.objects.exists()
    assert RelatorioConsolidadoDRE.objects.first().status == RelatorioConsolidadoDRE.STATUS_GERADO_PARCIAL
