import pytest

from sme_ptrf_apps.receitas.models import Receita

pytestmark = pytest.mark.django_db


def test_instance(receita):
    model = receita
    assert isinstance(model, Receita)
    assert model.associacao
    assert model.data
    assert model.valor
    assert model.descricao
    assert model.conta_associacao
    assert model.acao_associacao
    assert model.tipo_receita
    assert model.conferido


def test_str(receita):
    assert str(receita) == "RECEITA<Uma receita - 2020-03-26 - 100.0>"

def test_marcar_conferido(receita_nao_conferida):
    receita_nao_conferida.marcar_conferido()
    receita = Receita.objects.get(id=receita_nao_conferida.id)
    assert receita.conferido

def test_desmarcar_conferido(receita_conferida):
    receita_conferida.desmarcar_conferido()
    receita = Receita.objects.get(id=receita_conferida.id)
    assert not receita.conferido

