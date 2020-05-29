import pytest
from django.contrib import admin

from ...models import Despesa
from ...status_cadastro_completo import STATUS_COMPLETO

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
    assert model.documento_transacao is not None
    assert model.data_transacao
    assert model.valor_total
    assert model.valor_recursos_proprios
    assert model.valor_ptrf
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status == STATUS_COMPLETO


def test_srt_model(despesa):
    assert despesa.__str__() == '123456 - 2020-03-10 - 100.00'


def test_meta_modelo(despesa):
    assert despesa._meta.verbose_name == 'Despesa'
    assert despesa._meta.verbose_name_plural == 'Despesas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Despesa]


def test_nome_fornecedor_pode_ser_nulo(associacao, tipo_documento, tipo_transacao):
    # Criando sem definir o nome do fornecedor
    despesa = Despesa(associacao=associacao,
                      numero_documento='123456',
                      tipo_documento=tipo_documento,
                      cpf_cnpj_fornecedor='11.478.276/0001-04',
                      tipo_transacao=tipo_transacao,
                      valor_total=100.00,
                      valor_recursos_proprios=10.00, )
    despesa.save()
    assert despesa.numero_documento == '123456'
