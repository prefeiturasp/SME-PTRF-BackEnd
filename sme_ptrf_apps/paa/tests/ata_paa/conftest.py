import pytest
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from sme_ptrf_apps.core.fixtures.factories import FlagFactory


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
