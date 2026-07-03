import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r01_rateios_obrigatorios import RateiosObrigatoriosValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return RateiosObrigatoriosValidator()


def test_valida_ok_com_rateios(validator):
    ctx = make_ctx(rateios=[{"valor_rateio": 100}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_lista_vazia(validator):
    ctx = make_ctx(rateios=[])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "rateios" in exc_info.value.detail
