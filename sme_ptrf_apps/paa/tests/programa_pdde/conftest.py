import pytest
from model_bakery import baker

from sme_ptrf_apps.paa.models import ProgramaPdde
from sme_ptrf_apps.paa.admin import ProgramaPddeAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def programa_pdde_admin():
    return ProgramaPddeAdmin(model=ProgramaPdde, admin_site=site)


@pytest.fixture
def programa_pdde():
    return baker.make(
        'ProgramaPdde',
        nome='Programa PDDE Teste',
    )


@pytest.fixture
def programa_pdde_2():
    return baker.make(
        'ProgramaPdde',
        nome='Programa PDDE Teste 2',
    )


@pytest.fixture
def programa_pdde_3():
    return baker.make(
        'ProgramaPdde',
        nome='Programa PDDE Teste 3',
    )


@pytest.fixture
def acao_pdde(programa_pdde):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste',
        programa=programa_pdde,
    )


@pytest.fixture
def acao_pdde_2(programa_pdde_2):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste 2',
        programa=programa_pdde_2,
    )


@pytest.fixture
def acao_pdde_3(programa_pdde_2):
    return baker.make(
        'AcaoPdde',
        nome='Ação PDDE Teste 3',
        programa=programa_pdde_2,
    )
