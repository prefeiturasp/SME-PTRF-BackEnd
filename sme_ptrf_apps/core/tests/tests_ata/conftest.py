import pytest
from sme_ptrf_apps.core.models import Ata
from sme_ptrf_apps.core.admin import AtaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def ata_admin():
    return AtaAdmin(model=Ata, admin_site=site)
