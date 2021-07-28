import pytest
from django.contrib import admin

from ...models import RelatorioConsolidadoDRE
from ....core.models import Unidade, Periodo, TipoConta

pytestmark = pytest.mark.django_db


def test_instance_model(relatorio_dre_consolidado_gerado_total):
    model = relatorio_dre_consolidado_gerado_total
    assert isinstance(model, RelatorioConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.tipo_conta, TipoConta)
    assert model.status
    assert model.arquivo


def test_str_model(relatorio_dre_consolidado_gerado_total):
    assert relatorio_dre_consolidado_gerado_total.__str__() == 'Documento final gerado dia 27/10/2020 13:59'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[RelatorioConsolidadoDRE]
