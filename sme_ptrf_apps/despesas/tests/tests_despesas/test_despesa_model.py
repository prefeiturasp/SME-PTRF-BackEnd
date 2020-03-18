import pytest

from django.contrib import admin

from ...models import Despesa

pytestmark = pytest.mark.django_db


def test_instance_model(despesa):
    model = despesa
    assert isinstance(model, Despesa)
    assert model.associacao
    assert model.numero_documento
    assert model.tipo_documento
    assert model.cpf_cnpj_fornecedor
    assert model.nome_fornecedor
    assert model.tipo_transacao
    assert model.data_transacao
    assert model.valor_total
    assert model.valor_recursos_proprios
    assert model.valor_ptrf
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status


def test_srt_model(despesa):
    assert despesa.__str__() == '123456 - 2020-03-10 - 100.00'


def test_meta_modelo(despesa):
    assert despesa._meta.verbose_name == 'Despesa'
    assert despesa._meta.verbose_name_plural == 'Despesas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Despesa]
