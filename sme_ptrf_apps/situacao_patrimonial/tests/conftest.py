import pytest

from django.contrib.admin.sites import site

from sme_ptrf_apps.situacao_patrimonial.admin import BemProduzidoAdmin
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido

@pytest.fixture
def flag_situacao_patrimonial(flag_factory):
    return flag_factory.create(name='situacao-patrimonial')


@pytest.fixture
def bem_produzido_admin():
    return BemProduzidoAdmin(model=BemProduzido, admin_site=site)

@pytest.fixture
def bem_produzido_1(bem_produzido_factory):
    return bem_produzido_factory.create()