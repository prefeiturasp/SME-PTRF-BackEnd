from datetime import date
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest

from sme_ptrf_apps.core.models import PrestacaoConta, TipoAcertoDocumento
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida import PeriodoPcDevolvidaValidator

from .conftest import make_ctx


pytestmark = pytest.mark.django_db


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
    # Create normal (sem acerto): sem instância, só injeta ctx.periodo
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


def _criar_solicitacao_inclusao_gasto(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
):
    prestacao = prestacao_conta_factory(
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        periodo=periodo_2020_2,
        associacao=associacao,
    )
    analise_prestacao = analise_prestacao_conta_factory(prestacao_conta=prestacao)
    analise_documento = analise_documento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
    )
    tipo_acerto = tipo_acerto_documento_factory(
        categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
    )
    return solicitacao_acerto_documento_factory(
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto,
    ), prestacao


def test_create_acerto_ok_data_no_periodo_da_devolucao(
    validator,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
):
    solicitacao, _ = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
    )
    data = periodo_2020_2.data_inicio_realizacao_despesas
    ctx = make_ctx(
        is_create=True,
        data_transacao=data,
        recurso=periodo_2020_2.recurso,
        despesa_instance=None,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    assert validator.validate(ctx) is ctx
    assert ctx.periodo is not None
    assert ctx.periodo.referencia == periodo_2020_2.referencia


def test_create_acerto_bloqueia_data_fora_do_periodo_da_devolucao(
    validator,
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
    periodo_2020_1,
):
    solicitacao, _ = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
    )
    # Data no período 2020.1, PC da devolução é 2020.2
    data_fora = periodo_2020_1.data_inicio_realizacao_despesas
    ctx = make_ctx(
        is_create=True,
        data_transacao=data_fora,
        recurso=periodo_2020_1.recurso,
        despesa_instance=None,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    with pytest.raises(DespesaValidationError) as exc:
        validator.validate(ctx)
    assert "devolução" in exc.value.detail["mensagem"]


def test_create_acerto_uuid_inexistente_nao_bloqueia(validator, recurso_legado):
    """Sem PC resolvível, não aplica REG-007 (REG-069 cobre contexto inválido)."""
    periodo_mock = SimpleNamespace(referencia="2020.1")
    ctx = make_ctx(
        is_create=True,
        data_transacao=date(2020, 3, 10),
        recurso=recurso_legado,
        despesa_instance=None,
        uuid_solicitacao_acerto=str(uuid4()),
    )
    with patch("sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida.Periodo") as MockPeriodo:
        MockPeriodo.da_data_por_recurso.return_value = periodo_mock
        assert validator.validate(ctx) is ctx
