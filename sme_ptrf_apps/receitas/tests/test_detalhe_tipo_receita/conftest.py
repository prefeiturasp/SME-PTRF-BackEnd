import pytest

from sme_ptrf_apps.receitas.models.detalhe_tipo_receita import DetalheTipoReceita
from sme_ptrf_apps.receitas.admin import DetalheTipoReceitaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def detalhe_tipo_receita_admin():
    return DetalheTipoReceitaAdmin(model=DetalheTipoReceita, admin_site=site)
