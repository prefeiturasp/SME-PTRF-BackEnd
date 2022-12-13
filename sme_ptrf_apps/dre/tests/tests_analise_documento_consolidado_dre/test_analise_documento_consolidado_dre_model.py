import pytest
from django.contrib import admin
from ...models import AnaliseDocumentoConsolidadoDre, DocumentoAdicional, RelatorioConsolidadoDRE
from sme_ptrf_apps.core.models import Unidade, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(
    analise_documento_consolidado_dre_01,
    documento_adicional_consolidado_dre_01,
    relatorio_consolidado_dre_01,
):
    model = analise_documento_consolidado_dre_01
    assert isinstance(model, AnaliseDocumentoConsolidadoDre)
    assert isinstance(model.documento_adicional, DocumentoAdicional)
    assert isinstance(model.relatorio_consolidao_dre, RelatorioConsolidadoDRE)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.detalhamento is ''
    assert model.resultado


def test_str_model(analise_documento_consolidado_dre_01):
    assert analise_documento_consolidado_dre_01.__str__() == f"{analise_documento_consolidado_dre_01.analise_consolidado_dre.consolidado_dre.dre} - {analise_documento_consolidado_dre_01.analise_consolidado_dre.consolidado_dre.periodo} - Análise documento #{analise_documento_consolidado_dre_01.pk}"


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseDocumentoConsolidadoDre]

