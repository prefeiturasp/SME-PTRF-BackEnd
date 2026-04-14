import datetime

import pytest

from sme_ptrf_apps.core.services.ata_dados_service import formata_data

pytestmark = pytest.mark.django_db


def test_formata_data_retorna_separador_quando_nula():
    resultado = formata_data(None)
    assert resultado == ' - '


def test_formata_data_formata_corretamente():
    data = datetime.date(2020, 3, 26)
    resultado = formata_data(data)
    assert resultado == '26/03/2020'


def test_formata_data_mes_com_zero_a_esquerda():
    data = datetime.date(2021, 1, 5)
    resultado = formata_data(data)
    assert resultado == '05/01/2021'


def test_formata_data_ultimo_dia_do_ano():
    data = datetime.date(2020, 12, 31)
    resultado = formata_data(data)
    assert resultado == '31/12/2020'
