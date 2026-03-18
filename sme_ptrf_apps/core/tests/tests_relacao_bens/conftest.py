import pytest
from sme_ptrf_apps.core.models import RelacaoBens
from sme_ptrf_apps.core.admin import RelacaoBensAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def relacao_bens_admin():
    return RelacaoBensAdmin(model=RelacaoBens, admin_site=site)
