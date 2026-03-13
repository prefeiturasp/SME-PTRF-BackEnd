import pytest
from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
from sme_ptrf_apps.core.admin import DemonstrativoFinanceiroAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def demonstrativo_financeiro_admin():
    return DemonstrativoFinanceiroAdmin(model=DemonstrativoFinanceiro, admin_site=site)
