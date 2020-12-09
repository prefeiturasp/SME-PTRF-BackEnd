import pytest

from datetime import date

from django.contrib import admin
from model_bakery import baker

from ...models import PrestacaoConta, CobrancaPrestacaoConta, DevolucaoPrestacaoConta, Associacao, Periodo

pytestmark = pytest.mark.django_db

@pytest.fixture
def _cobranca_prestacao_devolucao(prestacao_conta_2020_1_conciliada, devolucao_prestacao_conta_2020_1):
    return baker.make(
        'CobrancaPrestacaoConta',
        prestacao_conta=prestacao_conta_2020_1_conciliada,
        tipo='DEVOLUCAO',
        data=date(2020, 7, 1),
        devolucao_prestacao=devolucao_prestacao_conta_2020_1
    )


def test_instance_model(_cobranca_prestacao_devolucao):
    model = _cobranca_prestacao_devolucao
    assert isinstance(model, CobrancaPrestacaoConta)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert model.tipo
    assert model.data
    assert isinstance(model.devolucao_prestacao, DevolucaoPrestacaoConta)


@pytest.fixture
def _cobranca_prestacao_recebimento_sem_pc(associacao, periodo):
    return baker.make(
        'CobrancaPrestacaoConta',
        associacao=associacao,
        periodo=periodo,
        tipo='RECEBIMENTO',
        data=date(2020, 7, 1),
    )


def test_instance_model_sem_pc(_cobranca_prestacao_recebimento_sem_pc):
    model = _cobranca_prestacao_recebimento_sem_pc
    assert isinstance(model, CobrancaPrestacaoConta)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.prestacao_conta is None
    assert model.tipo
    assert model.data


def test_srt_model(cobranca_prestacao_recebimento):
    assert cobranca_prestacao_recebimento.__str__() == '2020-07-01 - RECEBIMENTO'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[CobrancaPrestacaoConta]
