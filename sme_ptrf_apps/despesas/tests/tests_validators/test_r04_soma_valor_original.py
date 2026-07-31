from decimal import Decimal

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r04_soma_valor_original import SomaValorOriginalValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return SomaValorOriginalValidator()


def test_valida_ok_soma_exata(validator):
    ctx = make_ctx(
        valor_original=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_original": 100}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_com_recursos_proprios(validator):
    ctx = make_ctx(
        valor_original=Decimal("110.00"),
        valor_recursos_proprios=Decimal("10.00"),
        rateios=[{"valor_original": 100}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_valor_original_none_tratado_como_zero(validator):
    # valor_original=None → 0, recursos=0 → valor_original_real=0; rateio.valor_original=0 → ok
    ctx = make_ctx(
        valor_original=None,
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_original": 0}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_soma_incorreta(validator):
    ctx = make_ctx(
        valor_original=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        rateios=[{"valor_original": 80}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "rateios" in exc_info.value.detail


def test_valida_ok_com_imposto(validator):
    ctx = make_ctx(
        valor_original=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        retem_imposto=True,
        rateios=[{"valor_original": 80}],
        despesas_impostos=[{"valor_original": 20}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_com_imposto_soma_incorreta(validator):
    ctx = make_ctx(
        valor_original=Decimal("100.00"),
        valor_recursos_proprios=Decimal("0.00"),
        retem_imposto=True,
        rateios=[{"valor_original": 80}],
        despesas_impostos=[{"valor_original": 30}],
    )
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)
