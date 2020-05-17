from datetime import timedelta

import pytest

from sme_ptrf_apps.core.models import Periodo

pytestmark = pytest.mark.django_db

def test_periodo_da_data_metodo_encontrando_periodo(periodo, periodo_anterior):
    data_consultada = periodo.data_inicio_realizacao_despesas + timedelta(days=1)
    periodo_da_data = Periodo.da_data(data_consultada)
    assert periodo_da_data == periodo


def test_periodo_da_data_metodo_encontrando_periodo_data_inicial_limite(periodo, periodo_anterior):
    data_consultada = periodo.data_inicio_realizacao_despesas
    periodo_da_data = Periodo.da_data(data_consultada)
    assert periodo_da_data == periodo


def test_periodo_da_data_metodo_encontrando_periodo_data_final_limite(periodo, periodo_anterior):
    data_consultada = periodo.data_fim_realizacao_despesas
    periodo_da_data = Periodo.da_data(data_consultada)
    assert periodo_da_data == periodo


def test_periodo_da_data_metodo_encontrando_periodo_anterior(periodo, periodo_anterior):
    data_consultada = periodo_anterior.data_fim_realizacao_despesas
    periodo_da_data = Periodo.da_data(data_consultada)
    assert periodo_da_data == periodo_anterior


def test_periodo_da_data_metodo_nao_encontrando_periodo(periodo, periodo_anterior):
    data_consultada = periodo.data_fim_realizacao_despesas + timedelta(days=1)
    periodo_da_data = Periodo.da_data(data_consultada)
    assert periodo_da_data is None
