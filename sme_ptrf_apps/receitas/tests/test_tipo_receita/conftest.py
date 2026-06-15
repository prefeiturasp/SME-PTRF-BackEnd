import pytest
from django.contrib.admin.sites import site
from django.test import RequestFactory

from sme_ptrf_apps.receitas.admin import TipoReceitaAdmin
from sme_ptrf_apps.receitas.models import TipoReceita


@pytest.fixture
def tipo_receita_admin():
    return TipoReceitaAdmin(model=TipoReceita, admin_site=site)


@pytest.fixture
def admin_request():
    return RequestFactory().get('/admin/')
