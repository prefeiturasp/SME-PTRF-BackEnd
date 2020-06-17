import pytest
from django.contrib import admin

from ...models import Acao

pytestmark = pytest.mark.django_db


def test_instance_model(acao):
    model = acao
    assert isinstance(model, Acao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.posicao_nas_pesquisas


def test_srt_model(acao):
    assert acao.__str__() == 'PTRF'


def test_meta_modelo(acao):
    assert acao._meta.verbose_name == 'Ação'
    assert acao._meta.verbose_name_plural == 'Ações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Acao]
