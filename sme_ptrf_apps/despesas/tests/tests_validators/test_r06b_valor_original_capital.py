from decimal import Decimal

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r06b_valor_original_capital import ValorOriginalCapitalValidator

from .conftest import make_ctx

CAPITAL = "CAPITAL"
CUSTEIO = "CUSTEIO"


@pytest.fixture
def validator():
    return ValorOriginalCapitalValidator()


def test_valida_ok_rateio_custeio_ignorado(validator):
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CUSTEIO}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_sem_valor_item_ignorado(validator):
    # valor_item_capital ausente/falsy → ignora rateio
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 2, "valor_item_capital": None}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_calculo_correto(validator):
    # 2 × 50 = 100 == valor_original
    ctx = make_ctx(rateios=[{
        "aplicacao_recurso": CAPITAL,
        "quantidade_itens_capital": 2,
        "valor_item_capital": Decimal("50.00"),
        "valor_original": Decimal("100.00"),
    }])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_calculo_incorreto(validator):
    # 2 × 50 = 100 ≠ 80
    ctx = make_ctx(rateios=[{
        "aplicacao_recurso": CAPITAL,
        "quantidade_itens_capital": 2,
        "valor_item_capital": Decimal("50.00"),
        "valor_original": Decimal("80.00"),
    }])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


def test_valida_ok_multiplos_rateios_todos_corretos(validator):
    ctx = make_ctx(rateios=[
        {"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 1, "valor_item_capital": Decimal("200.00"), "valor_original": Decimal("200.00")},
        {"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 3, "valor_item_capital": Decimal("10.00"), "valor_original": Decimal("30.00")},
    ])
    result = validator.validate(ctx)
    assert result is ctx
