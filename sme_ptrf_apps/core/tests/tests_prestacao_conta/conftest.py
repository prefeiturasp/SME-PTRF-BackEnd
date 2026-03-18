import pytest
from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.core.admin import PrestacaoContaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def prestacao_conta_admin():
    return PrestacaoContaAdmin(model=PrestacaoConta, admin_site=site)
