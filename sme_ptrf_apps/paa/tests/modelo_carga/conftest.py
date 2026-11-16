import pytest
from model_bakery import baker

from sme_ptrf_apps.paa.models import ModeloCargaPaa
from sme_ptrf_apps.paa.enums import TipoCargaPaaEnum
from sme_ptrf_apps.paa.admin import ModeloCargaPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def modelo_carga_paa_admin():
    return ModeloCargaPaaAdmin(model=ModeloCargaPaa, admin_site=site)


@pytest.fixture
def modelo_carga_paa_plano_anual():
    return baker.make('ModeloCargaPaa', tipo_carga=TipoCargaPaaEnum.MODELO_PLANO_ANUAL.name)


@pytest.fixture(params=[None, ""], ids=['none', 'string_vazia'])
def tipo_carga_vazio(request):
    """Valores de tipo_carga ausentes que devem resultar em erro 400 no download."""
    return request.param


@pytest.fixture(params=[
    ("modelo_plano_anual.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("modelo_plano_anual.csv", "text/csv"),
    ("modelo_plano_anual.extensao_desconhecida", "application/octet-stream"),
], ids=['xlsx', 'csv', 'extensao_desconhecida'])
def nome_arquivo_e_content_type_esperado(request):
    """Retorna a tupla (nome_arquivo, content_type_esperado) para o download do modelo de carga."""
    return request.param
