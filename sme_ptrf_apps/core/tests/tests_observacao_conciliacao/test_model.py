import pytest
from django.contrib import admin

from sme_ptrf_apps.core.models import AcaoAssociacao, ObservacaoConciliacao, Periodo, ContaAssociacao, Associacao

pytestmark = pytest.mark.django_db


def test_model(observacao_conciliacao):
    model = observacao_conciliacao

    assert isinstance(model, ObservacaoConciliacao)
    assert isinstance(model.periodo, Periodo)
    assert isinstance(model.conta_associacao, ContaAssociacao)
    assert isinstance(model.associacao, Associacao)
    assert model.texto == "Uma bela observação."
    assert model.data_extrato
    assert model.saldo_extrato


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[ObservacaoConciliacao]
