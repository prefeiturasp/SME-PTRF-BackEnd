from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from sme_ptrf_apps.core.api.views.atas_viewset import AtasViewSet
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


@pytest.fixture
def gerar_arquivo_ata_com_campos_validos():
    """Retorna uma função que chama o endpoint gerar-arquivo-ata com a validação de campos aprovada.

    A função recebe (usuario, pc, ata) e retorna (response, mock_task), onde mock_task é o mock
    de `gerar_arquivo_ata_async`, para verificar se a geração foi enfileirada.
    """
    def _gerar(usuario, pc, ata):
        request = APIRequestFactory().get(f'/?prestacao-de-conta-uuid={pc.uuid}&ata-uuid={ata.uuid}')
        force_authenticate(request, user=usuario)
        view = AtasViewSet.as_view({'get': 'gerar_arquivo_ata'})

        with patch(
            'sme_ptrf_apps.core.api.views.atas_viewset.validar_campos_ata',
            return_value={'is_valid': True, 'campos': []},
        ), patch('sme_ptrf_apps.core.api.views.atas_viewset.gerar_arquivo_ata_async') as mock_task:
            response = view(request)

        return response, mock_task

    return _gerar
