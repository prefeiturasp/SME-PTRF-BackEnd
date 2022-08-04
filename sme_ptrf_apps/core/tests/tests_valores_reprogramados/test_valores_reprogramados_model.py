import pytest
from django.contrib import admin
from ...models import ValoresReprogramados

pytestmark = pytest.mark.django_db


def test_instance_model(valores_reprogramados_valores_corretos):
    model = valores_reprogramados_valores_corretos
    assert isinstance(model, ValoresReprogramados)
    assert model.associacao
    assert model.periodo
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.aplicacao_recurso
    assert model.valor_ue
    assert model.valor_dre
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ValoresReprogramados]

