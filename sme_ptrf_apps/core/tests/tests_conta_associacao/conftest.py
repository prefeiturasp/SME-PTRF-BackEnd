import pytest
from sme_ptrf_apps.core.models import ContaAssociacao
from sme_ptrf_apps.core.admin import ContaAssociacaoAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def conta_associacao_admin():
    return ContaAssociacaoAdmin(model=ContaAssociacao, admin_site=site)
