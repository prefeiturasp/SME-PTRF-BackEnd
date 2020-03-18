import pytest

from django.contrib import admin

from ...models import ContaAssociacao

pytestmark = pytest.mark.django_db


def test_instance_model(conta_associacao):
    model = conta_associacao
    assert isinstance(model, ContaAssociacao)
    assert model.associacao
    assert model.tipo_conta
    assert model.status
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id


def test_srt_model(conta_associacao):
    assert conta_associacao.__str__() == 'Escola Teste - Conta Cheque - Ativa'


def test_meta_modelo(conta_associacao):
    assert conta_associacao._meta.verbose_name == 'Conta de Associação'
    assert conta_associacao._meta.verbose_name_plural == 'Contas de Associações'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ContaAssociacao]
