import pytest

from sme_ptrf_apps.despesas.validators.r68_rateio_associacao import RateioAssociacaoValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return RateioAssociacaoValidator()


def test_validate_e_noop(validator):
    rateio = {"associacao": "outra", "valor_rateio": 10}
    ctx = make_ctx(associacao="assoc-ue", rateios=[rateio])
    result = validator.validate(ctx)
    assert result is ctx
    assert rateio["associacao"] == "outra"


def test_apply_sobrescreve_associacao_dos_rateios(validator):
    rateio_a = {"associacao": "outra", "valor_rateio": 50}
    rateio_b = {"valor_rateio": 50}
    associacao = object()
    ctx = make_ctx(associacao=associacao, rateios=[rateio_a, rateio_b])

    result = validator.apply(ctx)

    assert result is ctx
    assert rateio_a["associacao"] is associacao
    assert rateio_b["associacao"] is associacao


def test_apply_com_lista_vazia_nao_falha(validator):
    ctx = make_ctx(associacao=object(), rateios=[])
    result = validator.apply(ctx)
    assert result.rateios == []
