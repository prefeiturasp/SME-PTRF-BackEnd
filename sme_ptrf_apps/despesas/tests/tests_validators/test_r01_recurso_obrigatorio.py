import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r01_recurso_obrigatorio import RecursoObrigatorioValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return RecursoObrigatorioValidator()


def test_valida_ok_com_recurso(validator):
    ctx = make_ctx(recurso="PTRF")
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_recurso_none(validator):
    ctx = make_ctx(recurso=None)
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "Recurso" in str(exc_info.value.detail)


def test_valida_erro_recurso_string_vazia(validator):
    ctx = make_ctx(recurso="")
    with pytest.raises(DespesaValidationError):
        validator.validate(ctx)
