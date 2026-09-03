from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r70_associacao_imutavel import (
    MSG_ASSOCIACAO_IMUTAVEL,
    AssociacaoImutavelValidator,
)

from .conftest import make_ctx


@pytest.fixture
def validator():
    return AssociacaoImutavelValidator()


def test_valida_ok_sem_instancia(validator):
    ctx = make_ctx(despesa_instance=None, associacao=SimpleNamespace(pk=1))
    assert validator.validate(ctx) is ctx


def test_valida_ok_mesma_associacao_por_pk(validator):
    associacao = SimpleNamespace(pk=859)
    ctx = make_ctx(
        associacao=associacao,
        despesa_instance=SimpleNamespace(associacao=SimpleNamespace(pk=859)),
    )
    assert validator.validate(ctx) is ctx


def test_valida_ok_mesma_associacao_por_uuid(validator):
    uuid = "c3f45c8e-4634-4705-95f6-de6f97729ffd"
    ctx = make_ctx(
        associacao=SimpleNamespace(pk=None, uuid=uuid),
        despesa_instance=SimpleNamespace(associacao=SimpleNamespace(pk=None, uuid=uuid)),
    )
    assert validator.validate(ctx) is ctx


def test_valida_ok_associacao_payload_ausente(validator):
    ctx = make_ctx(
        associacao=None,
        despesa_instance=SimpleNamespace(associacao=SimpleNamespace(pk=859)),
    )
    assert validator.validate(ctx) is ctx


def test_valida_erro_associacao_diferente(validator):
    ctx = make_ctx(
        associacao=SimpleNamespace(pk=859),
        despesa_instance=SimpleNamespace(associacao=SimpleNamespace(pk=1573)),
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert exc_info.value.detail["mensagem"] == MSG_ASSOCIACAO_IMUTAVEL
    assert exc_info.value.detail["validator"] == "AssociacaoImutavelValidator"
