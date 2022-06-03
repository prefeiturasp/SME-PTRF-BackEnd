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
    assert not model.data_retorno_ue


def test_srt_model(devolucao_prestacao_conta_2020_1):
    assert devolucao_prestacao_conta_2020_1.__str__() == '2020-07-01 - 2020-08-01'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[DevolucaoPrestacaoConta]


def test_audit_log(devolucao_prestacao_conta_2020_1):
    assert devolucao_prestacao_conta_2020_1.history.count() == 1  # Um log de inclusão
    assert devolucao_prestacao_conta_2020_1.history.latest().action == 0  # 0-Inclusão

    devolucao_prestacao_conta_2020_1.data_limite_ue = "2022-06-03"
    devolucao_prestacao_conta_2020_1.save()
    assert devolucao_prestacao_conta_2020_1.history.count() == 2  # Um log de inclusão e outro de edição
    assert devolucao_prestacao_conta_2020_1.history.latest().action == 1  # 1-Edição

