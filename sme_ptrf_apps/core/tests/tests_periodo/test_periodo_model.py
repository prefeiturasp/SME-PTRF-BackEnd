import pytest
from django.contrib import admin

from ...models import Periodo

pytestmark = pytest.mark.django_db


def test_instance_model(periodo):
    model = periodo
    assert isinstance(model, Periodo)
    assert model.data_inicio_realizacao_despesas
    assert model.data_fim_realizacao_despesas
    assert model.data_prevista_repasse
    assert model.data_inicio_prestacao_contas
    assert model.data_fim_prestacao_contas
    assert model.uuid
    assert model.id


def test_srt_model(periodo):
    assert periodo.__str__() == '2019-09-01 a 2019-11-30'


def test_meta_modelo(periodo):
    assert periodo._meta.verbose_name == 'Período'
    assert periodo._meta.verbose_name_plural == 'Períodos'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Periodo]


def test_encadeamento_de_periodos(periodo, periodo_anterior):
    assert periodo.periodo_anterior == periodo_anterior
    assert periodo_anterior.proximo_periodo == periodo
