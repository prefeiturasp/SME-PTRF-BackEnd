import pytest
from django.contrib import admin

from ...models import TipoTransacao

pytestmark = pytest.mark.django_db


def test_instance_model(tipo_transacao):
    model = tipo_transacao
    assert isinstance(model, TipoTransacao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.tem_documento is not None


def test_srt_model(tipo_transacao):
    assert tipo_transacao.__str__() == 'Boleto'


def test_meta_modelo(tipo_transacao):
    assert tipo_transacao._meta.verbose_name == 'Tipo de transação'
    assert tipo_transacao._meta.verbose_name_plural == 'Tipos de transação'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoTransacao]
