import pytest
from model_bakery import baker

from sme_ptrf_apps.core.models import RecursoProprioPaa
from sme_ptrf_apps.core.admin import RecursoProprioPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def recurso_proprios_paa_admin():
    return RecursoProprioPaaAdmin(model=RecursoProprioPaa, admin_site=site)


@pytest.fixture
def fonte_recurso_paa(fonte_recurso_paa_factory):
    return fonte_recurso_paa_factory.create(nome="Fonte recurso")


@pytest.fixture
def recurso_proprio_paa(recurso_proprio_paa_factory):
    return recurso_proprio_paa_factory.create()


@pytest.fixture
def flag_paa(flag_factory):
    return flag_factory.create(name='paa')
