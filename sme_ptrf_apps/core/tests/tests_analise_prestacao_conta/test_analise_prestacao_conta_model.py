import pytest
from django.contrib import admin

from ...models import PrestacaoConta, AnalisePrestacaoConta, DevolucaoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_instance_model(analise_prestacao_conta_2020_1):
    model = analise_prestacao_conta_2020_1
    assert isinstance(model, AnalisePrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.devolucao_prestacao_conta, DevolucaoPrestacaoConta)
    assert model.status == AnalisePrestacaoConta.STATUS_EM_ANALISE


def test_srt_model(analise_prestacao_conta_2020_1):
    assert analise_prestacao_conta_2020_1.__str__() == f'2020.1 - 2020-01-01 a 2020-06-30 - Análise #{analise_prestacao_conta_2020_1.id}'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[AnalisePrestacaoConta]
