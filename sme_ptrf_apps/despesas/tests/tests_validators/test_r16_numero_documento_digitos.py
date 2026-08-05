from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r16_numero_documento_digitos import (
    NumeroDocumentoDigitosValidator,
)

from .conftest import make_ctx


@pytest.fixture
def validator():
    return NumeroDocumentoDigitosValidator()


def test_valida_ok_sem_tipo(validator):
    ctx = make_ctx(tipo_documento=None, numero_documento="ABC")
    assert validator.validate(ctx) is ctx


def test_valida_ok_apenas_digitos_com_numero_numerico(validator):
    tipo = SimpleNamespace(apenas_digitos=True, numero_documento_digitado=True)
    ctx = make_ctx(tipo_documento=tipo, numero_documento="12345")
    assert validator.validate(ctx) is ctx


def test_valida_erro_apenas_digitos_com_letra(validator):
    tipo = SimpleNamespace(apenas_digitos=True, numero_documento_digitado=True)
    ctx = make_ctx(tipo_documento=tipo, numero_documento="12A45")
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "numero_documento" in exc_info.value.detail


def test_apply_zera_quando_tipo_nao_pede_digitacao(validator):
    tipo = SimpleNamespace(apenas_digitos=False, numero_documento_digitado=False)
    ctx = make_ctx(tipo_documento=tipo, numero_documento="999")
    result = validator.apply(ctx)
    assert result.numero_documento == ""
