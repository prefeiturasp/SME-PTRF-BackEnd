import pytest
from model_bakery import baker
from sme_ptrf_apps.core.choices import RepresentacaoCargo


@pytest.fixture
def ambiente():
    return baker.make(
        'Ambiente',
        prefixo='dev-sig-escola',
        nome='Ambiente de desenvolvimento',
    )


@pytest.fixture
def membros_apm_fixture_mock(membro_associacao_factory):
    membro_associacao_factory.create(
        representacao=RepresentacaoCargo.PAI_RESPONSAVEL.name,
        cpf="90700000086"
    )
