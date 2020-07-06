import pytest
from django.contrib import admin

from sme_ptrf_apps.core.models import AcaoAssociacao, Observacao, PrestacaoConta

pytestmark = pytest.mark.django_db


def test_model(observacao):
    model = observacao

    assert isinstance(model, Observacao)
    assert isinstance(model.prestacao_conta, PrestacaoConta)
    assert isinstance(model.acao_associacao, AcaoAssociacao)
    assert model.texto == "Uma bela observação."


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Observacao]
