from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r71_conta_acao_mesma_associacao import (
    MSG_CONTA_ACAO_ASSOCIACAO,
    MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO,
    ContaAcaoMesmaAssociacaoValidator,
)

from .conftest import make_ctx


@pytest.fixture
def validator():
    return ContaAcaoMesmaAssociacaoValidator()


def _assoc(pk):
    return SimpleNamespace(pk=pk)


def _conta(pk_associacao):
    return SimpleNamespace(associacao=_assoc(pk_associacao))


def _acao(pk_associacao):
    return SimpleNamespace(associacao=_assoc(pk_associacao))


def test_valida_ok_sem_associacao(validator):
    ctx = make_ctx(associacao=None, rateios=[{"conta_associacao": _conta(1)}])
    assert validator.validate(ctx) is ctx


def test_valida_ok_sem_conta_nem_acao(validator):
    ctx = make_ctx(associacao=_assoc(859), rateios=[{"conta_associacao": None, "acao_associacao": None}])
    assert validator.validate(ctx) is ctx


def test_valida_ok_conta_e_acao_da_mesma_associacao(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{
            "conta_associacao": _conta(1573),
            "acao_associacao": _acao(1573),
        }],
    )
    assert validator.validate(ctx) is ctx


def test_valida_erro_conta_de_outra_associacao(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{
            "conta_associacao": _conta(859),
            "acao_associacao": _acao(1573),
        }],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail["mensagem"] == MSG_CONTA_ACAO_ASSOCIACAO


def test_valida_erro_acao_de_outra_associacao(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{
            "conta_associacao": _conta(1573),
            "acao_associacao": _acao(859),
        }],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail["mensagem"] == MSG_CONTA_ACAO_ASSOCIACAO


def test_valida_erro_imposto_associacao_diferente(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{"conta_associacao": _conta(1573), "acao_associacao": _acao(1573)}],
        despesas_impostos=[{"associacao": _assoc(859), "rateios": []}],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail["mensagem"] == MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO


def test_valida_erro_conta_de_imposto_de_outra_associacao(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{"conta_associacao": _conta(1573)}],
        despesas_impostos=[{
            "associacao": _assoc(1573),
            "rateios": [{"conta_associacao": _conta(859), "acao_associacao": _acao(1573)}],
        }],
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail["mensagem"] == MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO


def test_valida_ok_imposto_da_mesma_associacao(validator):
    ctx = make_ctx(
        associacao=_assoc(1573),
        rateios=[{"conta_associacao": _conta(1573), "acao_associacao": _acao(1573)}],
        despesas_impostos=[{
            "associacao": _assoc(1573),
            "rateios": [{"conta_associacao": _conta(1573), "acao_associacao": _acao(1573)}],
        }],
    )
    assert validator.validate(ctx) is ctx
