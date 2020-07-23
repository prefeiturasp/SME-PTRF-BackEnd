import pytest

from sme_ptrf_apps.receitas.models import TipoReceita

pytestmark = pytest.mark.django_db

def test_instance(tipo_receita):
    model = tipo_receita
    assert isinstance(model, TipoReceita)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert not model.e_repasse
    assert not model.aceita_capital
    assert not model.aceita_custeio
    assert not model.aceita_livre
    assert not model.e_devolucao


def test_srt_model(tipo_receita):
    assert str(tipo_receita) == 'Estorno'


def test_meta_modelo(tipo_receita):
    assert tipo_receita._meta.verbose_name == 'Tipo de receita'
    assert tipo_receita._meta.verbose_name_plural == 'Tipos de receita'
