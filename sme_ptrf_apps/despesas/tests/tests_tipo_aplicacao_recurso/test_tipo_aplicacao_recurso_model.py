import pytest

from django.contrib import admin

from ...models import TipoAplicacaoRecurso

pytestmark = pytest.mark.django_db


def test_instance_model(tipo_aplicacao_recurso):
    model = tipo_aplicacao_recurso
    assert isinstance(model, TipoAplicacaoRecurso)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(tipo_aplicacao_recurso):
    assert tipo_aplicacao_recurso.__str__() == 'Custeio'


def test_meta_modelo(tipo_aplicacao_recurso):
    assert tipo_aplicacao_recurso._meta.verbose_name == 'Tipo de aplicação de recurso'
    assert tipo_aplicacao_recurso._meta.verbose_name_plural == 'Tipos de aplicação de recursos'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoAplicacaoRecurso]
