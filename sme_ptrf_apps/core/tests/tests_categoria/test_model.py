import pytest


from django.contrib import admin
from model_bakery import baker
from ...models import Categoria

pytestmark = pytest.mark.django_db


@pytest.fixture
def categoria():
    return baker.make('Categoria', nome='Prestações de conta')


def test_instance_model(categoria):
    model = categoria
    assert isinstance(model, Categoria)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(categoria):
    assert str(categoria) == 'Prestações de conta'


def test_meta_modelo(categoria):
    assert categoria._meta.verbose_name == 'Categoria'
    assert categoria._meta.verbose_name_plural == 'Categorias'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Categoria]
