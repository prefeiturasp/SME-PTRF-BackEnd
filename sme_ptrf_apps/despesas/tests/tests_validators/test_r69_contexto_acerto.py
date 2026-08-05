"""Testes REG-069 — contexto de acerto (PC devolvida + solicitação pendente)."""
import datetime
from uuid import uuid4

import pytest

from sme_ptrf_apps.core.models import (
    AnaliseLancamentoPrestacaoConta,
    PrestacaoConta,
    SolicitacaoAcertoDocumento,
    SolicitacaoAcertoLancamento,
    TipoAcertoDocumento,
    TipoAcertoLancamento,
)
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r69_contexto_acerto import (
    ContextoAcertoValidator,
    MSG_CONTEXTO_ACERTO_INVALIDO,
)
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx


pytestmark = pytest.mark.django_db


def _criar_solicitacao_inclusao_gasto(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    status_solicitacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE,
    categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
):
    prestacao = prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )
    analise_prestacao = analise_prestacao_conta_factory(prestacao_conta=prestacao)
    analise_documento = analise_documento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
    )
    tipo_acerto = tipo_acerto_documento_factory(categoria=categoria)
    return solicitacao_acerto_documento_factory(
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto,
        status_realizacao=status_solicitacao,
    )


def _criar_edicao_pendente(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    lancamento_atualizado=False,
    status_solicitacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    status_analise=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
):
    prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )
    analise_prestacao = analise_prestacao_conta_factory()
    tipo_acerto = tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
    )
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        valor_total=50.00,
    )
    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
        despesa=despesa,
        lancamento_atualizado=lancamento_atualizado,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=status_analise,
    )
    solicitacao = solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=status_solicitacao,
    )
    return despesa, solicitacao


def test_create_ok_com_inclusao_gasto_pc_devolvida(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
):
    solicitacao = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
    )
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=str(solicitacao.uuid))
    assert ContextoAcertoValidator().validate(ctx) is ctx


def test_create_bloqueia_sem_pc_devolvida(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
):
    solicitacao = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_EM_ANALISE,
    )
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=str(solicitacao.uuid))
    with pytest.raises(DespesaValidationError) as exc:
        ContextoAcertoValidator().validate(ctx)
    assert MSG_CONTEXTO_ACERTO_INVALIDO in str(exc.value.detail)


def test_create_bloqueia_solicitacao_ja_realizada(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    associacao,
    periodo_2020_2,
):
    solicitacao = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
        status_solicitacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO,
    )
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=str(solicitacao.uuid))
    with pytest.raises(DespesaValidationError):
        ContextoAcertoValidator().validate(ctx)


def test_create_bloqueia_uuid_inexistente():
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=str(uuid4()))
    with pytest.raises(DespesaValidationError):
        ContextoAcertoValidator().validate(ctx)


def test_update_ok_com_edicao_pendente(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, solicitacao = _criar_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )
    ctx = make_ctx(
        is_create=False,
        despesa_instance=despesa,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    assert ContextoAcertoValidator().validate(ctx) is ctx


def test_update_ok_apos_marcar_realizado_com_pc_devolvida(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    """Re-edição durante devolução mesmo após marcar o acerto como realizado."""
    despesa, solicitacao = _criar_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        lancamento_atualizado=True,
        status_solicitacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_REALIZADO,
        status_analise=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO,
    )
    ctx = make_ctx(
        is_create=False,
        despesa_instance=despesa,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    assert ContextoAcertoValidator().validate(ctx) is ctx


def test_update_ok_com_inclusao_gasto_ja_vinculada(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    """Despesa criada via INCLUSAO_GASTO pode ser re-editada na devolução."""
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        valor_total=50.00,
    )
    solicitacao = _criar_solicitacao_inclusao_gasto(
        prestacao_conta_factory,
        analise_prestacao_conta_factory,
        analise_documento_prestacao_conta_factory,
        tipo_acerto_documento_factory,
        solicitacao_acerto_documento_factory,
        associacao,
        periodo_2020_2,
        status_solicitacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO,
    )
    solicitacao.despesa_incluida = despesa
    solicitacao.save()

    ctx = make_ctx(
        is_create=False,
        despesa_instance=despesa,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    assert ContextoAcertoValidator().validate(ctx) is ctx


def test_update_bloqueia_sem_pc_devolvida(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, solicitacao = _criar_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_EM_ANALISE,
    )
    ctx = make_ctx(
        is_create=False,
        despesa_instance=despesa,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
    )
    with pytest.raises(DespesaValidationError):
        ContextoAcertoValidator().validate(ctx)


def test_update_bloqueia_uuid_que_nao_bate(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _ = _criar_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )
    ctx = make_ctx(
        is_create=False,
        despesa_instance=despesa,
        uuid_solicitacao_acerto=str(uuid4()),
    )
    with pytest.raises(DespesaValidationError):
        ContextoAcertoValidator().validate(ctx)


def test_sem_acerto_nao_valida():
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=None)
    assert ContextoAcertoValidator().validate(ctx) is ctx
