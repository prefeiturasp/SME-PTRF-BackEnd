import pytest
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.core.admin import AcaoAssociacaoAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def acao_associacao_admin():
    return AcaoAssociacaoAdmin(model=AcaoAssociacao, admin_site=site)
