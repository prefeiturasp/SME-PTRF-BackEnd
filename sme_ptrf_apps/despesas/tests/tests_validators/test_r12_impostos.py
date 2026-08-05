import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r12_impostos import ImpostosValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return ImpostosValidator()


def test_valida_ok_sem_retem_imposto(validator):
    ctx = make_ctx(retem_imposto=False, despesas_impostos=[{"rateios": []}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_retem_imposto_com_rateios(validator):
    ctx = make_ctx(
        retem_imposto=True,
        despesas_impostos=[{"rateios": [{"valor_rateio": 20}]}],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_retem_imposto_multiplos_impostos_com_rateios(validator):
    ctx = make_ctx(
        retem_imposto=True,
        despesas_impostos=[
            {"rateios": [{"valor_rateio": 10}]},
            {"rateios": [{"valor_rateio": 20}]},
        ],
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_retem_imposto_sem_rateios(validator):
    ctx = make_ctx(
        retem_imposto=True,
        despesas_impostos=[{"rateios": []}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


def test_valida_erro_para_no_primeiro_imposto_invalido(validator):
    ctx = make_ctx(
        retem_imposto=True,
        despesas_impostos=[
            {"rateios": []},
            {"rateios": [{"valor_rateio": 20}]},
        ],
    )
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)
