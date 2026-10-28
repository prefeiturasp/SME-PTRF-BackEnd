import pytest
from sme_ptrf_apps.core.models import Ata
from sme_ptrf_apps.core.admin import AtaAdmin
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from django.contrib.admin.sites import site


@pytest.fixture
def ata_admin():
    return AtaAdmin(model=Ata, admin_site=site)


@pytest.fixture
def flag_historico_membros():
    return FlagFactory.create(
        name='historico-de-membros',
        everyone=True
    )


@pytest.fixture
def flag_historico_membros_v2():
    return FlagFactory.create(
        name='historico-de-membros-v2',
        everyone=True
    )


@pytest.fixture
def presentes_ata_com_presidente_e_secretario():
    """Retorna uma função que monta os presentes (presidente, secretária e conselheiro) da ata informada."""
    return lambda ata: [
        {
            'ata': ata,
            'identificacao': '1234567',
            'nome': 'João Silva',
            'cargo': 'Presidente da diretoria executiva',
            'presidente_da_reuniao': True,
            'secretario_da_reuniao': False,
            'membro': True,
            'professor_gremio': False,
            'presente': True
        },
        {
            'ata': ata,
            'identificacao': '7654321',
            'nome': 'Maria Santos',
            'cargo': 'Secretária',
            'presidente_da_reuniao': False,
            'secretario_da_reuniao': True,
            'membro': True,
            'professor_gremio': False,
            'presente': True
        },
        {
            'ata': ata,
            'identificacao': '1111111',
            'nome': 'Carlos Souza',
            'cargo': 'Conselheiro',
            'presidente_da_reuniao': False,
            'secretario_da_reuniao': False,
            'membro': True,
            'professor_gremio': False,
            'presente': True
        },
    ]
