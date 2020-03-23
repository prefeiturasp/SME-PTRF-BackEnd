import pytest
from django.test import RequestFactory
from model_bakery import baker

from sme_ptrf_apps.users.models import User
from sme_ptrf_apps.users.tests.factories import UserFactory

from .core.models.conta_associacao import ContaAssociacao
from .core.models.acao_associacao import AcaoAssociacao


@pytest.fixture
def fake_user(client, django_user_model):
    password = 'teste'
    username = 'fake'
    user = django_user_model.objects.create_user(username=username, password=password, )
    client.login(username=username, password=password)
    return user


@pytest.fixture
def authenticated_client(client, django_user_model):
    password = 'teste'
    username = 'fake'
    django_user_model.objects.create_user(username=username, password=password, )
    client.login(username=username, password=password)
    return client


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def tipo_conta():
    return baker.make('TipoConta', nome='Cheque')


@pytest.fixture
def acao():
    return baker.make('Acao', nome='PTRF')


@pytest.fixture
def associacao():
    return baker.make('Associacao', nome='Escola Teste')


@pytest.fixture
def conta_associacao(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta
    )


@pytest.fixture
def conta_associacao_inativa(associacao, tipo_conta):
    return baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta,
        status=ContaAssociacao.STATUS_INATIVA
    )


@pytest.fixture
def acao_associacao(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao
    )


@pytest.fixture
def acao_associacao_inativa(associacao, acao):
    return baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao,
        status=AcaoAssociacao.STATUS_INATIVA
    )
