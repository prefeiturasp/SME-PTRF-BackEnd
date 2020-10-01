import pytest
from django.contrib import admin

from ...models import PrestacaoConta, AnaliseContaPrestacaoConta, ContaAssociacao

pytestmark = pytest.mark.django_db


def test_instance_model(analise_conta_prestacao_conta_2020_1):
    model = analise_conta_prestacao_conta_2020_1
    assert isinstance(model, AnaliseContaPrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert model.data_extrato
    assert model.saldo_extrato


def test_srt_model(analise_conta_prestacao_conta_2020_1):
    assert analise_conta_prestacao_conta_2020_1.__str__() == 'Escola Teste - Conta Cheque - Ativa - 2020-07-01 - 100.0'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnaliseContaPrestacaoConta]
