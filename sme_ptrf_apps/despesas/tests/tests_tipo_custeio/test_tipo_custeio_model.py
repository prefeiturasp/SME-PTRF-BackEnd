import pytest

from django.contrib import admin

from ...models import TipoCusteio

pytestmark = pytest.mark.django_db


def test_instance_model(tipo_custeio):
    model = tipo_custeio
    assert isinstance(model, TipoCusteio)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_custeio):
    assert tipo_custeio.__str__() == 'Material'


def test_meta_modelo(tipo_custeio):
    assert tipo_custeio._meta.verbose_name == 'Tipo de custeio'
    assert tipo_custeio._meta.verbose_name_plural == 'Tipos de custeio'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoCusteio]
