import pytest
from django.contrib import admin

from ...models import JustificativaRelatorioConsolidadoDRE
from ....core.models import Unidade, Periodo, TipoConta

pytestmark = pytest.mark.django_db


def test_instance_model(justificativa_relatorio_dre_consolidado):
    model = justificativa_relatorio_dre_consolidado
    assert isinstance(model, JustificativaRelatorioConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.tipo_conta, TipoConta)
    assert model.texto

def test_str_model(justificativa_relatorio_dre_consolidado):
    assert justificativa_relatorio_dre_consolidado.__str__() == 'Teste'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[JustificativaRelatorioConsolidadoDRE]
