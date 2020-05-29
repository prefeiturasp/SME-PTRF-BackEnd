import pytest
from django.contrib import admin

from ...models import PrestacaoConta, Associacao, Periodo, ContaAssociacao
from ...models.prestacao_conta import STATUS_FECHADO as PRESTACAO_FECHADA

pytestmark = pytest.mark.django_db


def test_instance_model(prestacao_conta, prestacao_conta_anterior):
    model = prestacao_conta
    assert isinstance(model, PrestacaoConta)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert isinstance(model.prestacao_de_conta_anterior, PrestacaoConta)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status == PRESTACAO_FECHADA
    assert model.conciliado_em
    assert model.motivo_reabertura


def test_srt_model(prestacao_conta):
    assert prestacao_conta.__str__() == '2019.2 - 2019-09-01 a 2019-11-30 - Cheque  - FECHADO'


def test_meta_modelo(prestacao_conta):
    assert prestacao_conta._meta.verbose_name == 'Prestação de conta'
    assert prestacao_conta._meta.verbose_name_plural == 'Prestações de contas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrestacaoConta]
