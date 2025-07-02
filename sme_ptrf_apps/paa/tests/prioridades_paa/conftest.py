import pytest
from model_bakery import baker
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.admin import PrioridadePaaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def prioridade_paa_admin():
    return PrioridadePaaAdmin(model=PrioridadePaa, admin_site=site)


@pytest.fixture
def especificacao_material():
    return baker.make('EspecificacaoMaterialServico', descricao='Material teste')


@pytest.fixture
def programa_pdde():
    return baker.make('ProgramaPdde')


@pytest.fixture
def acao_pdde():
    return baker.make('AcaoPdde')
