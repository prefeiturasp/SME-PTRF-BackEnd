"""Testes REG-019 — período fechado (existe PC no período da data)."""
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r19_periodo_fechado import (
    MSG_PERIODO_FECHADO,
    PeriodoFechadoValidator,
)
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx


pytestmark = pytest.mark.django_db


@pytest.fixture
def validator():
    return PeriodoFechadoValidator()


def test_ok_sem_data(validator):
    ctx = make_ctx(
        data_transacao=None,
        associacao=SimpleNamespace(),
        recurso=SimpleNamespace(),
    )
    assert validator.validate(ctx) is ctx


def test_ok_sem_pc_no_periodo(validator):
    associacao = SimpleNamespace()
    recurso = SimpleNamespace()
    periodo = SimpleNamespace()
    ctx = make_ctx(
        data_transacao=date(2020, 3, 10),
        associacao=associacao,
        recurso=recurso,
    )
    with patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.Periodo") as MockPeriodo, \
         patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.PrestacaoConta") as MockPC:
        MockPeriodo.da_data_por_recurso.return_value = periodo
        MockPC.by_periodo.return_value = None
        assert validator.validate(ctx) is ctx
        MockPC.by_periodo.assert_called_once_with(associacao=associacao, periodo=periodo)


def test_bloqueia_quando_existe_pc(validator):
    associacao = SimpleNamespace()
    recurso = SimpleNamespace()
    periodo = SimpleNamespace()
    ctx = make_ctx(
        data_transacao=date(2020, 3, 10),
        associacao=associacao,
        recurso=recurso,
    )
    with patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.Periodo") as MockPeriodo, \
         patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.PrestacaoConta") as MockPC:
        MockPeriodo.da_data_por_recurso.return_value = periodo
        MockPC.by_periodo.return_value = SimpleNamespace(uuid="pc")
        with pytest.raises(DespesaValidationError) as exc:
            validator.validate(ctx)
    assert MSG_PERIODO_FECHADO in str(exc.value.detail)
    assert exc.value.detail["data_transacao"] == MSG_PERIODO_FECHADO


def test_nao_aplica_em_fluxo_acerto(validator):
    ctx = make_ctx(
        data_transacao=date(2020, 3, 10),
        associacao=SimpleNamespace(),
        recurso=SimpleNamespace(),
        uuid_solicitacao_acerto="acerto-uuid",
    )
    with patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.PrestacaoConta") as MockPC:
        assert validator.validate(ctx) is ctx
        MockPC.by_periodo.assert_not_called()


def test_bloqueia_data_imposto_em_periodo_com_pc(validator):
    associacao = SimpleNamespace()
    recurso = SimpleNamespace()
    periodo = SimpleNamespace()
    ctx = make_ctx(
        data_transacao=date(2020, 1, 10),
        associacao=associacao,
        recurso=recurso,
        retem_imposto=True,
        despesas_impostos=[{"data_transacao": date(2020, 3, 10)}],
    )
    with patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.Periodo") as MockPeriodo, \
         patch("sme_ptrf_apps.despesas.validators.r19_periodo_fechado.PrestacaoConta") as MockPC:
        MockPeriodo.da_data_por_recurso.side_effect = lambda data, rec: (
            None if data == date(2020, 1, 10) else periodo
        )
        MockPC.by_periodo.return_value = SimpleNamespace(uuid="pc")
        with pytest.raises(DespesaValidationError) as exc:
            validator.validate(ctx)
    assert exc.value.detail["despesa_imposto_data_transacao"] == MSG_PERIODO_FECHADO


def test_integracao_bloqueia_com_pc_real(
    validator,
    prestacao_conta_factory,
    associacao,
    periodo_2020_2,
    recurso_factory,
):
    prestacao_conta_factory(
        periodo=periodo_2020_2,
        associacao=associacao,
    )
    recurso = recurso_factory()
    # Garante que a data cai no periodo_2020_2
    data = periodo_2020_2.data_inicio_realizacao_despesas
    ctx = make_ctx(
        data_transacao=data,
        associacao=associacao,
        recurso=recurso,
    )
    # Periodo.da_data_por_recurso precisa achar o periodo — patch se recurso/periodo
    # não estiverem ligados no factory.
    with patch(
        "sme_ptrf_apps.despesas.validators.r19_periodo_fechado.Periodo.da_data_por_recurso",
        return_value=periodo_2020_2,
    ):
        with pytest.raises(DespesaValidationError):
            validator.validate(ctx)


def test_integracao_ok_sem_pc(
    validator,
    associacao,
    periodo_2020_2,
    recurso_factory,
):
    recurso = recurso_factory()
    data = periodo_2020_2.data_inicio_realizacao_despesas
    ctx = make_ctx(
        data_transacao=data,
        associacao=associacao,
        recurso=recurso,
    )
    with patch(
        "sme_ptrf_apps.despesas.validators.r19_periodo_fechado.Periodo.da_data_por_recurso",
        return_value=periodo_2020_2,
    ):
        assert validator.validate(ctx) is ctx
