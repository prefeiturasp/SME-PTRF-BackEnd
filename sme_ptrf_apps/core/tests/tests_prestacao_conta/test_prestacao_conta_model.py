import pytest
from django.contrib import admin

from ...models import PrestacaoConta, Associacao, Periodo
from ...models.prestacao_conta import STATUS_FECHADO as PRESTACAO_FECHADA

pytestmark = pytest.mark.django_db


def test_instance_model(prestacao_conta):
    model = prestacao_conta
    assert isinstance(model, PrestacaoConta)
    assert isinstance(model.associacao, Associacao)
    assert isinstance(model.periodo, Periodo)
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.status == PRESTACAO_FECHADA

def test_srt_model(prestacao_conta):
    assert prestacao_conta.__str__() == '2019.2 - 2019-09-01 a 2019-11-30 - FECHADO'


def test_meta_modelo(prestacao_conta):
    assert prestacao_conta._meta.verbose_name == 'Prestação de conta'
    assert prestacao_conta._meta.verbose_name_plural == 'Prestações de contas'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[PrestacaoConta]
