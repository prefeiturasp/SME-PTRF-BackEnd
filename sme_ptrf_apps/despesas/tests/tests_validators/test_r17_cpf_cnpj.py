import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r17_cpf_cnpj import CpfCnpjValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return CpfCnpjValidator()


def test_valida_ok_vazio(validator):
    ctx = make_ctx(cpf_cnpj_fornecedor="")
    assert validator.validate(ctx) is ctx


def test_valida_ok_cpf_formato(validator):
    ctx = make_ctx(cpf_cnpj_fornecedor="123.456.789-09")
    assert validator.validate(ctx) is ctx


def test_valida_erro_formato_invalido(validator):
    ctx = make_ctx(cpf_cnpj_fornecedor="123")
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "cpf_cnpj_fornecedor" in exc_info.value.detail
