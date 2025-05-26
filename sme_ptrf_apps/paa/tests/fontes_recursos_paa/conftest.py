import pytest

from sme_ptrf_apps.paa.models import FonteRecursoPaa
from sme_ptrf_apps.paa.admin import FonteRecursoPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def fonte_recurso_paa_admin():
    return FonteRecursoPaaAdmin(model=FonteRecursoPaa, admin_site=site)


@pytest.fixture
def fonte_recurso_paa(fonte_recurso_paa_factory):
    return fonte_recurso_paa_factory.create(nome="Fonte recurso")


@pytest.fixture
def flag_paa(flag_factory):
    return flag_factory.create(name='paa')
