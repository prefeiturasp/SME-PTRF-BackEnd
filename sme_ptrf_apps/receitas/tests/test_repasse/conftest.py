import pytest

from sme_ptrf_apps.receitas.models.repasse import Repasse
from sme_ptrf_apps.receitas.admin import RepasseAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def repasse_admin():
    return RepasseAdmin(model=Repasse, admin_site=site)
