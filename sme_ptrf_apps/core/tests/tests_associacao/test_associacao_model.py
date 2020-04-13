import pytest

from django.contrib import admin

from ...models import Associacao
from ....core.models import Unidade

pytestmark = pytest.mark.django_db


def test_instance_model(associacao):
    model = associacao
    assert isinstance(model, Associacao)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.cnpj
    assert model.presidente_associacao_nome
    assert model.presidente_associacao_rf
    assert model.presidente_conselho_fiscal_nome
    assert model.presidente_conselho_fiscal_rf
    assert isinstance(model.unidade, Unidade)


def test_srt_model(associacao):
    assert associacao.__str__() == 'Escola Teste'


def test_meta_modelo(associacao):
    assert associacao._meta.verbose_name == 'Associação'
    assert associacao._meta.verbose_name_plural == 'Associações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Associacao]
