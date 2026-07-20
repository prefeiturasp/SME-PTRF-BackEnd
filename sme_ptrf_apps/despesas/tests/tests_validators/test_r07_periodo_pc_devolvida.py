from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida import PeriodoPcDevolvidaValidator

from .conftest import make_ctx


@pytest.fixture
def validator():
    return PeriodoPcDevolvidaValidator()


def test_valida_ok_sem_data_transacao(validator):
    ctx = make_ctx(data_transacao=None, recurso="PTRF")
    result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_sem_recurso(validator):
    ctx = make_ctx(data_transacao=date(2020, 3, 10), recurso=None, despesa_instance=None)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = None
        result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_sem_despesa_instance_injeta_periodo(validator):
    # Sem instância de despesa, retorna após injetar ctx.periodo
    recurso = SimpleNamespace(nome="PTRF")
    periodo_mock = SimpleNamespace(referencia="2020.1")
    ctx = make_ctx(data_transacao=date(2020, 3, 10), recurso=recurso, despesa_instance=None)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        result = validator.validate(ctx)
    assert result.periodo is periodo_mock


def test_valida_ok_despesa_sem_prestacao_conta(validator):
    recurso = SimpleNamespace(nome="PTRF")
    periodo_mock = SimpleNamespace(referencia="2020.1")
    despesa = SimpleNamespace(prestacao_conta=None)
    ctx = make_ctx(data_transacao=date(2020, 3, 10), recurso=recurso, despesa_instance=despesa)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_pc_nao_devolvida(validator):
    recurso = SimpleNamespace(nome="PTRF")
    periodo_mock = SimpleNamespace(referencia="2020.1")
    pc = SimpleNamespace(devolvida_para_acertos=False, periodo=SimpleNamespace(referencia="2020.1"))
    despesa = SimpleNamespace(prestacao_conta=pc)
    ctx = make_ctx(data_transacao=date(2020, 3, 10), recurso=recurso, despesa_instance=despesa)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        result = validator.validate(ctx)
    assert result is ctx


def test_valida_ok_mesmo_periodo_pc_devolvida(validator):
    recurso = SimpleNamespace(nome="PTRF")
    periodo_mock = SimpleNamespace(referencia="2020.1")
    pc = SimpleNamespace(devolvida_para_acertos=True, periodo=SimpleNamespace(referencia="2020.1"))
    despesa = SimpleNamespace(prestacao_conta=pc)
    ctx = make_ctx(data_transacao=date(2020, 3, 10), recurso=recurso, despesa_instance=despesa)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        result = validator.validate(ctx)
    assert result is ctx


def test_valida_erro_periodo_divergente(validator):
    recurso = SimpleNamespace(nome="PTRF")
    periodo_mock = SimpleNamespace(referencia="2020.2")
    pc = SimpleNamespace(devolvida_para_acertos=True, periodo=SimpleNamespace(referencia="2020.1"))
    despesa = SimpleNamespace(prestacao_conta=pc)
    ctx = make_ctx(data_transacao=date(2020, 6, 10), recurso=recurso, despesa_instance=despesa)
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        with pytest.raises(DespesaValidationError) as exc_info:
            validator.validate(ctx)
    assert "mensagem" in exc_info.value.detail
