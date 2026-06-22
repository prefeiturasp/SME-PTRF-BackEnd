import pytest
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
