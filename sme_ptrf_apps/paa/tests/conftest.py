from datetime import date
import pytest

from django.contrib.admin.sites import site
from rest_framework.test import APIClient

from sme_ptrf_apps.paa.admin import PeriodoPaaAdmin, PaaAdmin, ParametroPaaAdmin
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa, ParametroPaa
from datetime import date


@pytest.fixture
def flag_paa(flag_factory):
    return flag_factory.create(name='paa')


@pytest.fixture
def periodo_paa_admin():
    return PeriodoPaaAdmin(model=PeriodoPaa, admin_site=site)


@pytest.fixture
def periodo_paa_1(periodo_paa_factory):
    return periodo_paa_factory.create(referencia="Periodo 04/2025 a 10/2025",
                                      data_inicial=date(2025, 4, 1),
                                      data_final=date(2025, 10, 31))


@pytest.fixture
def periodo_paa_2(periodo_paa_factory):
    return periodo_paa_factory.create(referencia="Periodo 11/2025 a 12/2025",
                                      data_inicial=date(2025, 11, 1),
                                      data_final=date(2025, 12, 31))


@pytest.fixture
def paa_admin():
    return PaaAdmin(model=Paa, admin_site=site)


@pytest.fixture
def parametro_paa_admin():
    return ParametroPaaAdmin(model=ParametroPaa, admin_site=site)


@pytest.fixture
def paa(paa_factory, periodo_paa_1, associacao):
    return paa_factory.create(periodo_paa=periodo_paa_1, associacao=associacao)


@pytest.fixture
def parametro_paa(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=4)
