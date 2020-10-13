import pytest
from django.contrib import admin

from ...models import PrestacaoConta, DevolucaoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_instance_model(devolucao_prestacao_conta_2020_1):
    model = devolucao_prestacao_conta_2020_1
    assert isinstance(model, DevolucaoPrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert model.data
    assert model.data_limite_ue


def test_srt_model(devolucao_prestacao_conta_2020_1):
    assert devolucao_prestacao_conta_2020_1.__str__() == '2020-07-01 - 2020-08-01'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[DevolucaoPrestacaoConta]
