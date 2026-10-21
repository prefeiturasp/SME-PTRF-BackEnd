import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r05_quantidade_capital import QuantidadeCapitalValidator

from .conftest import make_ctx

CAPITAL = "CAPITAL"
CUSTEIO = "CUSTEIO"


@pytest.fixture
def validator():
    return QuantidadeCapitalValidator()


def test_valida_ok_rateio_custeio_ignorado(validator):
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CUSTEIO, "quantidade_itens_capital": 0}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_capital_quantidade_positiva(validator):
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 2}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_capital_quantidade_zero(validator):
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 0}])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


def test_valida_erro_capital_quantidade_negativa(validator):
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": -1}])
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)


def test_valida_erro_capital_quantidade_none(validator):
    # None → or 0 → ≤ 0 → erro
    ctx = make_ctx(rateios=[{"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": None}])
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)


def test_valida_ok_mistura_custeio_e_capital_valido(validator):
    ctx = make_ctx(rateios=[
        {"aplicacao_recurso": CUSTEIO, "quantidade_itens_capital": 0},
        {"aplicacao_recurso": CAPITAL, "quantidade_itens_capital": 3},
    ])
    result = validator.validate(ctx)
    assert result is ctx
