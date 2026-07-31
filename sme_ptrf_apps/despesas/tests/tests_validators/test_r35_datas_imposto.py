from datetime import date, timedelta

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r35_datas_imposto import DatasImpostoValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return DatasImpostoValidator()


def test_ignora_sem_retencao(validator):
    ctx = make_ctx(
        retem_imposto=False,
        despesas_impostos=[{"data_transacao": date.today()}],
    )
    assert validator.validate(ctx) is ctx


def test_ok_imposto_na_mesma_data(validator):
    hoje = date.today()
    ctx = make_ctx(
        retem_imposto=True,
        data_transacao=hoje,
        despesas_impostos=[{"data_transacao": hoje}],
    )
    assert validator.validate(ctx) is ctx


def test_erro_imposto_sem_data_despesa(validator):
    ctx = make_ctx(
        retem_imposto=True,
        data_transacao=None,
        despesas_impostos=[{"data_transacao": date.today()}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "sem data de despesa" in exc_info.value.detail["despesa_imposto_data_transacao"]


def test_erro_imposto_antes_da_despesa(validator):
    ctx = make_ctx(
        retem_imposto=True,
        data_transacao=date.today(),
        despesas_impostos=[{"data_transacao": date.today() - timedelta(days=1)}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "menor que data da despesa" in exc_info.value.detail[
        "despesa_imposto_data_transacao"
    ]


def test_erro_imposto_futuro(validator):
    hoje = date.today()
    ctx = make_ctx(
        retem_imposto=True,
        data_transacao=hoje,
        despesas_impostos=[{"data_transacao": hoje + timedelta(days=1)}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "hoje" in exc_info.value.detail["despesa_imposto_data_transacao"]
