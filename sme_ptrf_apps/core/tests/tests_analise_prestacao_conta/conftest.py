import pytest
from sme_ptrf_apps.core.models import AnalisePrestacaoConta
from sme_ptrf_apps.core.admin import AnalisePrestacaoContaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def analise_prestacao_conta_admin():
    return AnalisePrestacaoContaAdmin(model=AnalisePrestacaoConta, admin_site=site)
