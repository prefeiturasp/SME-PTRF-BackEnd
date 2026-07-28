from datetime import date
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r10_datas_encerramento import DatasEncerramentoValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return DatasEncerramentoValidator()


def _associacao(data_encerramento):
    return SimpleNamespace(data_de_encerramento=data_encerramento)


def test_valida_ok_sem_associacao(validator):
    ctx = make_ctx(associacao=None, data_documento=date(2020, 3, 10), data_transacao=date(2020, 3, 10))
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_associacao_sem_encerramento(validator):
    ctx = make_ctx(
        associacao=_associacao(None),
        data_documento=date(2020, 3, 10),
        data_transacao=date(2020, 3, 10),
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_data_anterior_ao_encerramento(validator):
    ctx = make_ctx(
        associacao=_associacao(date(2021, 12, 31)),
        data_documento=date(2020, 3, 10),
        data_transacao=date(2020, 3, 10),
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_data_igual_ao_encerramento(validator):
    ctx = make_ctx(
        associacao=_associacao(date(2020, 3, 10)),
        data_documento=date(2020, 3, 10),
        data_transacao=date(2020, 3, 10),
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_data_documento_posterior_ao_encerramento(validator):
    ctx = make_ctx(
        associacao=_associacao(date(2020, 3, 1)),
        data_documento=date(2020, 3, 10),
        data_transacao=None,
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail.get("erro_data_de_encerramento") is True


def test_valida_erro_data_transacao_posterior_ao_encerramento(validator):
    ctx = make_ctx(
        associacao=_associacao(date(2020, 3, 1)),
        data_documento=None,
        data_transacao=date(2020, 3, 10),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail.get("erro_data_de_encerramento") is True
    assert "data_de_encerramento" in exc_info.value.detail
