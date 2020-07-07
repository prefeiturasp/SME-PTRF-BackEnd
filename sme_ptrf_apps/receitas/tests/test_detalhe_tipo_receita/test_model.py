import pytest

from sme_ptrf_apps.receitas.models import DetalheTipoReceita

pytestmark = pytest.mark.django_db

def test_instance(detalhe_tipo_receita, tipo_receita):
    model = detalhe_tipo_receita
    assert isinstance(model, DetalheTipoReceita)
    assert model.nome
    assert model.criado_em
    assert model.alterado_em
    assert model.uuid
    assert model.id
    assert model.tipo_receita == tipo_receita


def test_srt_model(tipo_receita):
    assert str(tipo_receita) == 'Estorno'


def test_meta_modelo(tipo_receita):
    assert tipo_receita._meta.verbose_name == 'Tipo de receita'
    assert tipo_receita._meta.verbose_name_plural == 'Tipos de receita'
