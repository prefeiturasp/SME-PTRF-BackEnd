import pytest
from model_bakery import baker
from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes

from sme_ptrf_apps.paa.admin import AtividadeEstatutariaAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def atividade_estatutaria_admin():
    return AtividadeEstatutariaAdmin(model=AtividadeEstatutaria, admin_site=site)


@pytest.fixture
def atividade_estatutaria_ativo():
    return baker.make('AtividadeEstatutaria',
                      nome="Atividade Estatutária 1",
                      status=True,
                      mes=Mes.JANEIRO,
                      tipo=TipoAtividadeEstatutariaEnum.ORDINARIA.name, paa=None)


@pytest.fixture
def atividade_estatutaria_inativo():
    return baker.make('AtividadeEstatutaria',
                      nome="Atividade Estatutária 2",
                      status=False,
                      mes=Mes.FEVEREIRO,
                      tipo=TipoAtividadeEstatutariaEnum.EXTRAORDINARIA.name, paa=None)
