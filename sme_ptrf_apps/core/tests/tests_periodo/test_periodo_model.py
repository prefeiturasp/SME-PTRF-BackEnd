import pytest
from django.contrib import admin
from freezegun import freeze_time

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
    assert model.referencia


def test_srt_model(periodo):
    assert periodo.__str__() == '2019.2 - 2019-09-01 a 2019-11-30'


def test_admin():
    # pylint: disable=W0212
    assert admin.site._registry[Periodo]


def test_encadeamento_de_periodos(periodo, periodo_anterior):
    assert periodo.periodo_anterior == periodo_anterior
    assert periodo_anterior.proximo_periodo == periodo

@freeze_time('2020-07-01 10:11:12')
def test_periodo_encerrado(periodo_fim_em_2020_06_30):
    assert periodo_fim_em_2020_06_30.encerrado

@freeze_time('2020-06-30 10:11:12')
def test_periodo_nao_encerrado(periodo_fim_em_2020_06_30):
    assert not periodo_fim_em_2020_06_30.encerrado

@freeze_time('2020-12-30 10:11:12')
def test_periodo_aberto_nao_encerrado(periodo_fim_em_aberto):
    assert not periodo_fim_em_aberto.encerrado
