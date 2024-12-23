import pytest

from django.contrib.auth import get_user_model


@pytest.fixture
def usuario():
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(
        username=login,
        password=senha,
        email=email
    )
    user.save()

    return user


@pytest.fixture
def associacoes(associacao_factory):
    associacao_factory.create()
    associacao_factory.create()


@pytest.fixture
def data_inicio():
    return "2024-12-01"


@pytest.fixture
def data_final():
    return "2024-12-31"
