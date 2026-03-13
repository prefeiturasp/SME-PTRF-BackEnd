import pytest
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.core.admin import AssociacaoAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def associacao_admin():
    return AssociacaoAdmin(model=Associacao, admin_site=site)
