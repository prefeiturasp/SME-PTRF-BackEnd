import pytest

from sme_ptrf_apps.core.models import AnaliseLancamentoPrestacaoConta

pytestmark = pytest.mark.django_db


def test_status_realizado(
    solicitacao_acerto_lancamento_status_realizado,
    solicitacao_acerto_lancamento_status_realizado_02
):
    analise = solicitacao_acerto_lancamento_status_realizado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO


def test_status_justificado(
    solicitacao_acerto_lancamento_status_justificado,
    solicitacao_acerto_lancamento_status_justificado_02
):
    analise = solicitacao_acerto_lancamento_status_justificado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_JUSTIFICADO


def test_status_nao_realizado(
    solicitacao_acerto_lancamento_status_nao_realizado,
    solicitacao_acerto_lancamento_status_nao_realizado_02
):
    analise = solicitacao_acerto_lancamento_status_nao_realizado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE


def test_status_realizado_justificado(
    solicitacao_acerto_lancamento_status_realizado,
    solicitacao_acerto_lancamento_status_justificado,
):
    analise = solicitacao_acerto_lancamento_status_realizado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_JUSTIFICADO


def test_status_realizado_parcialmente(
    solicitacao_acerto_lancamento_status_realizado,
    solicitacao_acerto_lancamento_status_nao_realizado,
):
    analise = solicitacao_acerto_lancamento_status_realizado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE


def test_status_realizado_parcialmente_nao_realizado_e_justificado(
    solicitacao_acerto_lancamento_status_justificado,
    solicitacao_acerto_lancamento_status_nao_realizado,
):
    analise = solicitacao_acerto_lancamento_status_justificado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == \
           AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE


def test_status_realizado_justificado_parcialmente(
    solicitacao_acerto_lancamento_status_realizado,
    solicitacao_acerto_lancamento_status_justificado,
    solicitacao_acerto_lancamento_status_nao_realizado,
):
    analise = solicitacao_acerto_lancamento_status_realizado.analise_lancamento
    analise.calcula_status_realizacao_analise_lancamento()

    assert analise.status_realizacao == \
           AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_REALIZADO_PARCIALMENTE
