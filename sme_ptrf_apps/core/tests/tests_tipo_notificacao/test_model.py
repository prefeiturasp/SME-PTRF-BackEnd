import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import TipoNotificacao

pytestmark = pytest.mark.django_db


@pytest.fixture
def tipo_notificacao():
    return baker.make('TipoNotificacao', nome='Informação')


def test_instance_model(tipo_notificacao):
    model = tipo_notificacao
    assert isinstance(model, TipoNotificacao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_notificacao):
    assert str(tipo_notificacao) == 'Informação'


def test_meta_modelo(tipo_notificacao):
    assert tipo_notificacao._meta.verbose_name == 'Tipo de notificação'
    assert tipo_notificacao._meta.verbose_name_plural == 'Tipos de notificação'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoNotificacao]
