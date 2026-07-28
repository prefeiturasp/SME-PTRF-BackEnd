from datetime import date
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r08_contas_impostos import ContasImpostosValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return ContasImpostosValidator()


def _conta(data_inicio=None, data_encerramento=None):
    return SimpleNamespace(data_inicio=data_inicio, data_encerramento=data_encerramento)


def test_valida_ok_sem_impostos(validator):
    ctx = make_ctx(despesas_impostos=[])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_imposto_sem_data_transacao(validator):
    ctx = make_ctx(despesas_impostos=[{"data_transacao": None, "rateios": [{"conta_associacao": _conta()}]}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_rateio_sem_conta(validator):
    ctx = make_ctx(despesas_impostos=[{
        "data_transacao": date(2020, 3, 10),
        "rateios": [{"conta_associacao": None}],
    }])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_dentro_do_intervalo(validator):
    ctx = make_ctx(despesas_impostos=[{
        "data_transacao": date(2020, 3, 10),
        "rateios": [{"conta_associacao": _conta(date(2020, 1, 1), date(2020, 12, 31))}],
    }])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_data_inicio_posterior(validator):
    ctx = make_ctx(despesas_impostos=[{
        "data_transacao": date(2020, 3, 10),
        "rateios": [{"conta_associacao": _conta(date(2020, 4, 1), None)}],
    }])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail
    assert "início" in exc_info.value.detail["mensagem"]


def test_valida_erro_data_encerramento_anterior(validator):
    ctx = make_ctx(despesas_impostos=[{
        "data_transacao": date(2020, 3, 10),
        "rateios": [{"conta_associacao": _conta(date(2020, 1, 1), date(2020, 2, 28))}],
    }])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail
    assert "encerramento" in exc_info.value.detail["mensagem"]
