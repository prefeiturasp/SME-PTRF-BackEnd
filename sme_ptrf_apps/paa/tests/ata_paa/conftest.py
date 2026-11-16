import pytest
from datetime import datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from django.utils import timezone
from sme_ptrf_apps.core.fixtures.factories import FlagFactory
from sme_ptrf_apps.paa.models import AtaPaa


@pytest.fixture
def usuario_task():
    User = get_user_model()
    return User.objects.create_user(
        username='usuario_task_test',
        password='senha123',
        email='task@teste.com'
    )


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
def mock_flag_model_com_flags_ativas():
    """Retorna uma função que monta o mock do model de flags do waffle com apenas as flags informadas ativas."""
    def _mock_flag_model(*nomes_flags_ativas):
        mock_flag_model = MagicMock()
        mock_flag_model.objects.filter.side_effect = (
            lambda name=None, **kwargs: MagicMock(exists=MagicMock(return_value=name in nomes_flags_ativas))
        )
        return mock_flag_model
    return _mock_flag_model


@pytest.fixture(params=[
    (AtaPaa.ATA_APRESENTACAO, 'Ata de Apresentação do PAA'),
    (AtaPaa.ATA_RETIFICACAO, 'Ata de Retificação do PAA'),
], ids=['apresentacao', 'retificacao'])
def tipo_ata_e_nome_esperado(request):
    """Retorna a tupla (tipo_ata, nome_esperado) para cada tipo de ata do PAA."""
    return request.param


@pytest.fixture(params=[
    None,
    timezone.make_aware(datetime(2025, 2, 5, 10, 30)),
], ids=['nao_preenchida', 'preenchida'])
def preenchida_em(request):
    """Retorna valores possíveis para o campo preenchida_em da ata do PAA."""
    return request.param


@pytest.fixture(params=[True, False], ids=['completa', 'incompleta'])
def ata_completa(request):
    """Retorna os valores possíveis para a propriedade completa da ata do PAA."""
    return request.param


@pytest.fixture(params=[True, False], ids=['precisa', 'nao_precisa'])
def precisa_professor_gremio(request):
    """Retorna os valores possíveis para a propriedade precisa_professor_gremio da ata do PAA."""
    return request.param


@pytest.fixture(params=[
    (None, '00:00'),
    ('', '00:00'),
    ('14:30:00', '14:30'),
    ('14:30', '14:30'),
    ('9:30', '9:30'),
    (time(14, 30), '14:30'),
    (time(0, 0), '00:00'),
], ids=[
    'sem_hora',
    'string_vazia',
    'string_com_segundos',
    'string_hh_mm',
    'string_menor_que_5_caracteres',
    'objeto_time',
    'objeto_time_meia_noite',
])
def hora_reuniao_e_esperado(request):
    """Retorna a tupla (hora_reuniao, hora_esperada) cobrindo as condicionais de get_hora_reuniao."""
    return request.param


@pytest.fixture(params=[
    SimpleNamespace(paa=None),
    SimpleNamespace(paa=SimpleNamespace(associacao=None)),
], ids=['sem_paa', 'paa_sem_associacao'])
def ata_sem_associacao(request):
    """Retorna objetos de ata sem PAA ou com PAA sem associação."""
    return request.param
