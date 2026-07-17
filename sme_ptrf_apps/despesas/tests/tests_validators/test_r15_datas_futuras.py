from datetime import date, timedelta

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r15_datas_futuras import DatasFuturasValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return DatasFuturasValidator()


def test_valida_ok_sem_datas(validator):
    ctx = make_ctx(data_documento=None, data_transacao=None)
    assert validator.validate(ctx) is ctx


def test_valida_ok_datas_hoje_ou_passado(validator):
    hoje = date.today()
    ctx = make_ctx(data_documento=hoje, data_transacao=hoje - timedelta(days=1))
    assert validator.validate(ctx) is ctx


def test_valida_erro_data_documento_futura(validator):
    ctx = make_ctx(
        data_documento=date.today() + timedelta(days=1),
        data_transacao=None,
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "data_documento" in exc_info.value.detail
    assert "hoje" in exc_info.value.detail["data_documento"]


def test_valida_erro_data_transacao_futura(validator):
    ctx = make_ctx(
        data_documento=None,
        data_transacao=date.today() + timedelta(days=2),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "data_transacao" in exc_info.value.detail


def test_valida_erro_ambas_futuras(validator):
    futuro = date.today() + timedelta(days=1)
    ctx = make_ctx(data_documento=futuro, data_transacao=futuro)
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "data_documento" in exc_info.value.detail
    assert "data_transacao" in exc_info.value.detail
