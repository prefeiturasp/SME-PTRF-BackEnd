import pytest
from model_bakery import baker
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.admin import PrioridadePaaAdmin
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
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


@pytest.fixture
def prioridade_paa_ptrf_custeio(paa, acao_associacao, especificacao_material_servico, tipo_custeio):
    import uuid
    return baker.make('PrioridadePaa',
                      uuid=uuid.uuid4(),
                      paa=paa,
                      prioridade=1,
                      recurso=RecursoOpcoesEnum.PTRF.name,
                      tipo_aplicacao=TipoAplicacaoOpcoesEnum.CUSTEIO.name,
                      acao_pdde=None,
                      programa_pdde=None,
                      acao_associacao=acao_associacao,
                      especificacao_material=especificacao_material_servico,
                      tipo_despesa_custeio=tipo_custeio,
                      valor_total=20
                      )
