from datetime import date

from sme_ptrf_apps.despesas.validators.r28_data_documento_vazia import (
    DataDocumentoVaziaValidator,
)

from .conftest import make_ctx


def test_apply_copia_data_transacao_quando_documento_vazio():
    validator = DataDocumentoVaziaValidator()
    dt = date(2024, 5, 10)
    ctx = make_ctx(data_transacao=dt, data_documento=None)
    result = validator.apply(ctx)
    assert result.data_documento == dt


def test_apply_nao_sobrescreve_documento_existente():
    validator = DataDocumentoVaziaValidator()
    ctx = make_ctx(
        data_transacao=date(2024, 5, 10),
        data_documento=date(2024, 5, 1),
    )
    result = validator.apply(ctx)
    assert result.data_documento == date(2024, 5, 1)


def test_apply_imposto_alinha_data_documento():
    validator = DataDocumentoVaziaValidator()
    dt = date(2024, 6, 1)
    imposto = {"data_transacao": dt, "data_documento": None}
    ctx = make_ctx(despesas_impostos=[imposto])
    validator.apply(ctx)
    assert imposto["data_documento"] == dt
