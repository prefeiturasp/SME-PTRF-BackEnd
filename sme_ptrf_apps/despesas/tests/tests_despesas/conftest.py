import pytest
from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.despesas.admin import DespesaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def despesas_admin():
    return DespesaAdmin(model=Despesa, admin_site=site)
