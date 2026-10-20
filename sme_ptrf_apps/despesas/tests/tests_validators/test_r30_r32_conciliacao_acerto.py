"""Testes REG-030/032 — conciliação apply em fluxo de acerto."""
from decimal import Decimal
from uuid import uuid4

import pytest

from sme_ptrf_apps.despesas.validators.r30_r32_conciliacao_acerto import ConciliacaoAcertoValidator
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx


pytestmark = pytest.mark.django_db


def test_create_acerto_concilia_rateios(solicitacao_acerto_documento_factory):
    solicitacao = solicitacao_acerto_documento_factory()
    periodo = (
        solicitacao.analise_documento
        .analise_prestacao_conta
        .prestacao_conta
        .periodo
    )
    rateio = {
        "aplicacao_recurso": "CUSTEIO",
        "valor_rateio": Decimal("50.00"),
        "conferido": False,
    }
    ctx = make_ctx(
        is_create=True,
        uuid_solicitacao_acerto=str(solicitacao.uuid),
        rateios=[rateio],
    )

    ConciliacaoAcertoValidator().apply(ctx)

    assert rateio["conferido"] is True
    assert rateio["update_conferido"] is True
    assert rateio["periodo_conciliacao"] == periodo


def test_create_sem_acerto_nao_concilia():
    rateio = {"conferido": False, "valor_rateio": Decimal("10")}
    ctx = make_ctx(is_create=True, uuid_solicitacao_acerto=None, rateios=[rateio])

    ConciliacaoAcertoValidator().apply(ctx)

    assert rateio["conferido"] is False
    assert "update_conferido" not in rateio


def test_update_acerto_concilia_apenas_rateios_novos_se_existentes_conciliados(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    from sme_ptrf_apps.core.models import (
        AnaliseLancamentoPrestacaoConta,
        PrestacaoConta,
        SolicitacaoAcertoLancamento,
        TipoAcertoLancamento,
    )
    import datetime

    prestacao_conta_factory(
        status=PrestacaoConta.STATUS_DEVOLVIDA,
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
        lancamento_atualizado=False,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
    )
    solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    )

    existente = {"uuid": str(uuid4()), "conferido": True, "valor_rateio": Decimal("20")}
    novo = {"conferido": False, "valor_rateio": Decimal("30")}
    ctx = make_ctx(
        is_create=False,
        uuid_solicitacao_acerto=str(uuid4()),
        despesa_instance=despesa,
        rateios=[existente, novo],
    )

    ConciliacaoAcertoValidator().apply(ctx)

    assert novo["conferido"] is True
    assert novo["update_conferido"] is True
    periodo_esperado = analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo
    assert novo["periodo_conciliacao"] == periodo_esperado
