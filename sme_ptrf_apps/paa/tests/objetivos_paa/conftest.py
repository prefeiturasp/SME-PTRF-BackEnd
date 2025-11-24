import pytest
from model_bakery import baker
from sme_ptrf_apps.paa.models import ObjetivoPaa
from sme_ptrf_apps.paa.admin import ObjetivoPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def objetivo_paa_admin():
    return ObjetivoPaaAdmin(model=ObjetivoPaa, admin_site=site)


@pytest.fixture
def objetivo_paa_ativo():
    return baker.make('ObjetivoPaa', nome="Objetivo 1", status=True, paa=None)


@pytest.fixture
def objetivo_paa_inativo():
    return baker.make('ObjetivoPaa', nome="Objetivo 2", status=False)


@pytest.fixture
def objetivo_paa_sem_paa():
    return baker.make('ObjetivoPaa', nome="Objetivo 3", paa=None)
