import pytest
from django.contrib import admin

from ...models import Unidade

from ..admin import UnidadeAdmin

pytestmark = pytest.mark.django_db


def test_instance_model(unidade):
    model = unidade
    assert isinstance(model, Unidade)
    assert isinstance(model.dre, Unidade)
    assert model.nome
    assert model.tipo_unidade
    assert model.codigo_eol
    assert model.sigla


def test_srt_model(unidade):
    assert unidade.__str__() == 'Escola Teste'


def test_meta_modelo(unidade):
    model = unidade
    assert model._meta.verbose_name == 'Unidade'
    assert model._meta.verbose_name_plural == 'Unidades'


def test_admin():
    model_admin = UnidadeAdmin(Unidade, admin.site)
    # pylint: disable=W0212
    assert admin.site._registry[Unidade]
    assert model_admin.list_display == ('nome', 'equipamento', 'tipo_unidade', 'codigo_eol', 'sigla', 'dre')
    assert model_admin.ordering == ('nome',)
    assert model_admin.search_fields == ('nome', 'codigo_eol', 'sigla')
    assert model_admin.list_filter == ('equipamento', 'tipo_unidade', 'dre')
