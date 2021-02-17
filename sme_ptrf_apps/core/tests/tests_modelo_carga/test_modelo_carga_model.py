import pytest

from django.contrib import admin

from ...models import ModeloCarga

pytestmark = pytest.mark.django_db


def test_instance_model(modelo_carga_associacao):
    model = modelo_carga_associacao
    assert isinstance(model, ModeloCarga)
    assert model.uuid
    assert model.tipo_carga
    assert model.arquivo
    assert model.criado_em
    assert model.alterado_em
    assert model.id


def test_srt_model(modelo_carga_associacao):
    assert modelo_carga_associacao.__str__() == 'Carga de Associações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ModeloCarga]
