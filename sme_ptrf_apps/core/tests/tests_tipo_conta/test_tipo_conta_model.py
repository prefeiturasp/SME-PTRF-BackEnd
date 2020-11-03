import pytest

from django.contrib import admin

from ...models import TipoConta

pytestmark = pytest.mark.django_db


def test_instance_model(tipo_conta):
    model = tipo_conta
    assert isinstance(model, TipoConta)
    assert model.uuid
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.banco_nome
    assert model.agencia
    assert model.numero_conta
    assert model.numero_cartao
    assert not model.apenas_leitura


def test_srt_model(tipo_conta):
    assert tipo_conta.__str__() == 'Cheque'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[TipoConta]
