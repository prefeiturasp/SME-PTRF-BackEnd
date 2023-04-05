import pytest
from django.contrib import admin
from ...models import AnaliseConsolidadoDre
from ...models.consolidado_dre import ConsolidadoDRE
from sme_ptrf_apps.core.models import Unidade, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(analise_consolidado_dre_01, consolidado_dre_teste_model_comentario_analise_consolidado_dre):
    model = analise_consolidado_dre_01
    assert isinstance(model, AnaliseConsolidadoDre)
    assert isinstance(model.consolidado_dre, ConsolidadoDRE)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.data_devolucao
    assert model.data_limite
    assert model.data_retorno_analise
    assert model.relatorio_acertos_versao
    assert model.relatorio_acertos_status
    assert model.relatorio_acertos_status
    assert model.relatorio_acertos_gerado_em

def test_str_model(analise_consolidado_dre_01):
    assert analise_consolidado_dre_01.__str__() == f"{analise_consolidado_dre_01.consolidado_dre.dre} - {analise_consolidado_dre_01.consolidado_dre.periodo} - Análise #{analise_consolidado_dre_01.pk}"

def test_admin():
    assert admin.site._registry[AnaliseConsolidadoDre]
