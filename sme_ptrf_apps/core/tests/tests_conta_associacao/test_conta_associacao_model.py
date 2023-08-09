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
    assert model.banco_nome
    assert model.agencia
    assert model.numero_conta
    assert model.numero_cartao


def test_criacao_modelo_com_valores_default(associacao, tipo_conta):
    conta = ContaAssociacao.objects.create(associacao=associacao, tipo_conta=tipo_conta, banco_nome="Banco BRB")

    assert conta.banco_nome == 'Banco BRB'
    assert conta.agencia == '67945'
    assert conta.numero_conta == '935556-x'
    assert conta.numero_cartao == '987644164221'


def test_srt_model(conta_associacao):
    assert conta_associacao.__str__() == 'Escola Teste - Conta Cheque - Ativa'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ContaAssociacao]


def test_get_valores(conta_associacao, tipo_conta, associacao):
    assert ContaAssociacao.get_valores().count() == 1


def test_get_valores_com_inativos(conta_associacao, conta_associacao_inativa, tipo_conta, associacao):
    assert ContaAssociacao.get_valores().count() == 2
