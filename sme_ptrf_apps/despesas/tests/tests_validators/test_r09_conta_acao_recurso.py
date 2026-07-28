from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r09_conta_acao_recurso import ContaAcaoRecursoValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return ContaAcaoRecursoValidator()


def _conta(recurso):
    return SimpleNamespace(tipo_conta=SimpleNamespace(recurso=recurso))


def _acao(recurso):
    return SimpleNamespace(acao=SimpleNamespace(recurso=recurso))


def test_valida_ok_sem_conta(validator):
    ctx = make_ctx(rateios=[{"conta_associacao": None, "acao_associacao": _acao("PTRF")}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_sem_acao(validator):
    ctx = make_ctx(rateios=[{"conta_associacao": _conta("PTRF"), "acao_associacao": None}])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_mesmo_recurso(validator):
    ctx = make_ctx(rateios=[{
        "conta_associacao": _conta("PTRF"),
        "acao_associacao": _acao("PTRF"),
    }])
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_recursos_diferentes(validator):
    ctx = make_ctx(rateios=[{
        "conta_associacao": _conta("PTRF"),
        "acao_associacao": _acao("ROLECULTURAL"),
    }])
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail


def test_valida_ok_recurso_conta_none(validator):
    # getattr chain retorna None → sem comparação → ok
    conta = SimpleNamespace(tipo_conta=SimpleNamespace(recurso=None))
    ctx = make_ctx(rateios=[{
        "conta_associacao": conta,
        "acao_associacao": _acao("PTRF"),
    }])
    result = validator.validate(ctx)
    assert result is ctx
