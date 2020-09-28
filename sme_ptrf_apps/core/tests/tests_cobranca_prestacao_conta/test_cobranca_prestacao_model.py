import pytest
from django.contrib import admin

from ...models import PrestacaoConta, CobrancaPrestacaoConta

pytestmark = pytest.mark.django_db


def test_instance_model(cobranca_prestacao_recebimento):
    model = cobranca_prestacao_recebimento
    assert isinstance(model, CobrancaPrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert model.tipo
    assert model.data


def test_srt_model(cobranca_prestacao_recebimento):
    assert cobranca_prestacao_recebimento.__str__() == '2020-07-01 - RECEBIMENTO'


def test_meta_modelo(cobranca_prestacao_recebimento):
    assert cobranca_prestacao_recebimento._meta.verbose_name == 'Cobrança de prestação de contas'
    assert cobranca_prestacao_recebimento._meta.verbose_name_plural == 'Cobranças de prestações de contas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[CobrancaPrestacaoConta]
