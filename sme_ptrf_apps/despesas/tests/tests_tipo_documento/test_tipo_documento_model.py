import pytest

from django.contrib import admin

from ...models import TipoDocumento

pytestmark = pytest.mark.django_db


def test_instance_model(tipo_documento):
    model = tipo_documento
    assert isinstance(model, TipoDocumento)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_documento):
    assert tipo_documento.__str__() == 'NFe'


def test_meta_modelo(tipo_documento):
    assert tipo_documento._meta.verbose_name == 'Tipo de documento'
    assert tipo_documento._meta.verbose_name_plural == 'Tipos de documento'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoDocumento]
