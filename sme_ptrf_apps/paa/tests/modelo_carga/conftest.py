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
