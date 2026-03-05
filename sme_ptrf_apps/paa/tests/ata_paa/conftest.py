import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def usuario_task():
    User = get_user_model()
    return User.objects.create_user(
        username='usuario_task_test',
        password='senha123',
        email='task@teste.com'
    )
