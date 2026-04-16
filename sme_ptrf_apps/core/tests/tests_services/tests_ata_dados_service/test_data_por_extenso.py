import datetime

import pytest

from sme_ptrf_apps.core.services.ata_dados_service import data_por_extenso

pytestmark = pytest.mark.django_db


def test_data_por_extenso_retorna_placeholder_quando_data_nula():
    resultado = data_por_extenso(None)
    assert resultado == 'Aos ___ dias do mês de ___ de ___'


def test_data_por_extenso_dia_1_usa_no_primeiro_dia():
    data = datetime.date(2020, 3, 1)
    resultado = data_por_extenso(data)
    assert resultado.startswith('No primeiro dia do mês de março de')


def test_data_por_extenso_dia_maior_que_1_usa_aos():
    data = datetime.date(2020, 3, 15)
    resultado = data_por_extenso(data)
    assert 'dias do mês de março de' in resultado


def test_data_por_extenso_mes_janeiro():
    data = datetime.date(2021, 1, 10)
    resultado = data_por_extenso(data)
    assert 'janeiro' in resultado


def test_data_por_extenso_mes_dezembro():
    data = datetime.date(2021, 12, 5)
    resultado = data_por_extenso(data)
    assert 'dezembro' in resultado


def test_data_por_extenso_todos_os_meses():
    meses_esperados = [
        (1, 'janeiro'), (2, 'fevereiro'), (3, 'março'), (4, 'abril'),
        (5, 'maio'), (6, 'junho'), (7, 'julho'), (8, 'agosto'),
        (9, 'setembro'), (10, 'outubro'), (11, 'novembro'), (12, 'dezembro'),
    ]
    for mes, nome_mes in meses_esperados:
        data = datetime.date(2020, mes, 15)
        resultado = data_por_extenso(data)
        assert nome_mes in resultado, f"Mês {mes} deveria conter '{nome_mes}'"


def test_data_por_extenso_contem_ano():
    data = datetime.date(2023, 6, 20)
    resultado = data_por_extenso(data)
    assert '2023' in resultado or 'dois mil' in resultado.lower()
