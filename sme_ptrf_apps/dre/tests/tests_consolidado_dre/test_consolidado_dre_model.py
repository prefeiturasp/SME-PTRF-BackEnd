import pytest
from django.contrib import admin
from ...models import ConsolidadoDRE
from sme_ptrf_apps.core.models import Unidade, Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(consolidado_dre_teste_model_consolidado_dre, dre_teste_model_consolidado_dre, periodo_teste_model_consolidado_dre):
    model = consolidado_dre_teste_model_consolidado_dre
    assert isinstance(model, ConsolidadoDRE)
    assert isinstance(model.dre, Unidade)
    assert isinstance(model.periodo, Periodo)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.dre
    assert model.periodo
    assert model.status
    assert model.versao
    assert model.status_sme
    assert model.data_publicacao is None
    assert model.pagina_publicacao is ''


def test_str_model(consolidado_dre_teste_model_consolidado_dre):
    assert consolidado_dre_teste_model_consolidado_dre.__str__() == 'Documentos não gerados'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ConsolidadoDRE]
