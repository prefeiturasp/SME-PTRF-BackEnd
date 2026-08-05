import pytest

from sme_ptrf_apps.despesas.validators.r20_saldos import SaldosValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return SaldosValidator()


def test_valida_ok_sempre_passthrough(validator):
    # considerar_na_pipeline=False → retorna ctx imediatamente sem qualquer verificação
    ctx = make_ctx()
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_passthrough_com_associacao_e_data(validator):
    from types import SimpleNamespace
    from datetime import date
    ctx = make_ctx(
        associacao=SimpleNamespace(uuid="alguma-uuid"),
        data_transacao=date(2020, 3, 10),
    )
    result = validator.validate(ctx)
    assert result is ctx
