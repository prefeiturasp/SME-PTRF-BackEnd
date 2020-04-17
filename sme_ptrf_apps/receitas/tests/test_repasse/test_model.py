import pytest

from sme_ptrf_apps.receitas.models import Repasse

pytestmark = pytest.mark.django_db


def test_model(repasse):
    model = repasse
    assert isinstance(repasse, Repasse)
    assert model.associacao
    assert model.periodo
    assert model.valor_capital
    assert model.valor_custeio
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.status == 'PENDENTE'


def test_str(repasse):
    assert str(repasse) == "Repasse<val_capital: 1000.28, val_custeio: 1000.4>"
