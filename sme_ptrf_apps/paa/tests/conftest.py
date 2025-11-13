import pytest
from datetime import date

from django.contrib.admin.sites import site
from rest_framework.test import APIClient

from sme_ptrf_apps.paa.admin import (
    PeriodoPaaAdmin, PaaAdmin, ParametroPaaAdmin
)
from sme_ptrf_apps.paa.models import (
    PeriodoPaa, Paa, ParametroPaa
)


@pytest.fixture
def flag_paa(flag_factory):
    return flag_factory.create(name='paa')


@pytest.fixture
def periodo_paa_admin():
    return PeriodoPaaAdmin(model=PeriodoPaa, admin_site=site)


@pytest.fixture
def periodo_2025_1(periodo_factory):
    return periodo_factory.create(
        referencia='2025.1',
        data_inicio_realizacao_despesas=date(2025, 1, 1),
        data_fim_realizacao_despesas=date(2025, 4, 30),
    )


@pytest.fixture
def periodo_paa_2025_1(periodo_paa_factory, periodo_2025_1):
    return periodo_paa_factory.create(referencia="Periodo 04/2025 a 10/2025",
                                      data_inicial=date(2025, 1, 1),
                                      data_final=date(2025, 4, 30))


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
def periodo_paa_resumo_recursos(periodo_paa_factory):
    return periodo_paa_factory.create(referencia=f"Periodo 01/{date.today().year} a 12/{date.today().year}",
                                      data_inicial=date(date.today().year, 1, 1),
                                      data_final=date(date.today().year, 12, 31))


@pytest.fixture
def resumo_recursos_paa(paa_factory, periodo_paa_resumo_recursos, associacao):
    return paa_factory.create(periodo_paa=periodo_paa_resumo_recursos, associacao=associacao)


@pytest.fixture
def parametro_paa(parametro_paa_factory):
    return parametro_paa_factory.create(mes_elaboracao_paa=4)


@pytest.fixture
def ata_paa(ata_paa_factory, paa):
    return ata_paa_factory.create(paa=paa)


@pytest.fixture
def presente_ata_paa_membro(participante_ata_paa_factory, ata_paa):
    return participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        identificacao="123",
        nome="membro",
        cargo="teste cargo",
        membro=True,
        conselho_fiscal=False,
        professor_gremio=False
    )


@pytest.fixture
def presente_ata_paa_nao_membro(participante_ata_paa_factory, ata_paa):
    return participante_ata_paa_factory.create(
        ata_paa=ata_paa,
        identificacao="456",
        nome="nao membro",
        cargo="teste cargo",
        membro=False,
        conselho_fiscal=False,
        professor_gremio=False
    )
