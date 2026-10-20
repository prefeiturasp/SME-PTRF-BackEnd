from decimal import Decimal

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r03_soma_valor_rateio import SomaValorRateioValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return SomaValorRateioValidator()


def test_valida_ok_soma_exata(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_rateio": 100}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_com_recursos_proprios(validator):
    ctx = make_ctx(
        valor_total=Decimal("110.00"),
        valor_recursos_proprios=Decimal("10.00"),
        rateios=[{"valor_rateio": 100}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_multiplos_rateios(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_rateio": 60}, {"valor_rateio": 40}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_soma_maior_que_valor(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_rateio": 150}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "rateios" in exc_info.value.detail


def test_valida_erro_soma_menor_que_valor(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_rateio": 80}],
    )
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)


def test_valida_ok_com_imposto(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        retem_imposto=True,
        rateios=[{"valor_rateio": 80}],
        despesas_impostos=[{"valor_total": 20}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_com_imposto_soma_incorreta(validator):
    ctx = make_ctx(
        valor_total=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        retem_imposto=True,
        rateios=[{"valor_rateio": 80}],
        despesas_impostos=[{"valor_total": 30}],
    )
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)
