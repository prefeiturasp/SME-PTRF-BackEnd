from datetime import date

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r11_pagamento_antecipado import PagamentoAntecipadoValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return PagamentoAntecipadoValidator()


def test_valida_ok_sem_datas(validator):
    ctx = make_ctx(data_transacao=None, data_documento=None)
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_data_transacao_igual_documento(validator):
    ctx = make_ctx(data_transacao=date(2020, 3, 10), data_documento=date(2020, 3, 10))
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_data_transacao_posterior_ao_documento(validator):
    ctx = make_ctx(data_transacao=date(2020, 3, 15), data_documento=date(2020, 3, 10))
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_antecipado_com_motivos(validator):
    motivo = object()
    ctx = make_ctx(
        data_transacao=date(2020, 3, 5),
        data_documento=date(2020, 3, 10),
        motivos_pagamento_antecipado=[motivo],
        outros_motivos="",
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_antecipado_com_outros_motivos(validator):
    ctx = make_ctx(
        data_transacao=date(2020, 3, 5),
        data_documento=date(2020, 3, 10),
        motivos_pagamento_antecipado=[],
        outros_motivos="urgente",
    )
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_antecipado_sem_motivos(validator):
    ctx = make_ctx(
        data_transacao=date(2020, 3, 5),
        data_documento=date(2020, 3, 10),
        motivos_pagamento_antecipado=[],
        outros_motivos="",
    )
    with pytest.raises(DespesaValidationError) as exc_info:
        validator.validate(ctx)
    assert "detail" in exc_info.value.detail


def test_apply_nao_antecipado_zera_motivos(validator):
    motivo = object()
    ctx = make_ctx(
        data_transacao=date(2020, 3, 15),
        data_documento=date(2020, 3, 10),
        motivos_pagamento_antecipado=[motivo],
        outros_motivos="algum motivo",
    )
    result = validator.apply(ctx)
    assert result.motivos_pagamento_antecipado == []
    assert result.outros_motivos == ""


def test_apply_antecipado_mantem_motivos(validator):
    motivo = object()
    ctx = make_ctx(
        data_transacao=date(2020, 3, 5),
        data_documento=date(2020, 3, 10),
        motivos_pagamento_antecipado=[motivo],
        outros_motivos="urgente",
    )
    result = validator.apply(ctx)
    assert result.motivos_pagamento_antecipado == [motivo]
    assert result.outros_motivos == "urgente"


def test_apply_sem_datas_nao_altera(validator):
    motivo = object()
    ctx = make_ctx(
        data_transacao=None,
        data_documento=None,
        motivos_pagamento_antecipado=[motivo],
        outros_motivos="motivo",
    )
    result = validator.apply(ctx)
    assert result.motivos_pagamento_antecipado == [motivo]
    assert result.outros_motivos == "motivo"
