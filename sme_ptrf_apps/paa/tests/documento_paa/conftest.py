import pytest

from sme_ptrf_apps.paa.models import DocumentoPaa
from sme_ptrf_apps.paa.admin import DocumentoPaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def documento_paa_admin():
    return DocumentoPaaAdmin(model=DocumentoPaa, admin_site=site)


@pytest.fixture
def documento_paa(documento_paa_factory):
    return documento_paa_factory.create()
