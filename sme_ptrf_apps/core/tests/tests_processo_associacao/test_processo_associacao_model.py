import pytest

from ...models import ProcessoAssociacao, Associacao

pytestmark = pytest.mark.django_db


def test_instance_model(processo_associacao_123456_2019):
    model = processo_associacao_123456_2019
    assert isinstance(model, ProcessoAssociacao)
    assert isinstance(model.associacao, Associacao)
    assert model.numero_processo
    assert model.ano
    assert model.uuid


def test_admin():
    from django.contrib import admin
    assert admin.site._registry[ProcessoAssociacao]
