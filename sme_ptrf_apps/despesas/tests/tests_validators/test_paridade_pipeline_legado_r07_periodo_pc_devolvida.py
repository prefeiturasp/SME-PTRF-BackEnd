"""Paridade REG-007: ValidacaoDespesaService.validar_periodo_e_contas (legado, ainda
importável) vs PeriodoPcDevolvidaValidator, no fluxo de edição (despesa_instance presente).
"""
import datetime

import pytest
from rest_framework import serializers

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.despesas.services.validacao_despesa_service import ValidacaoDespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r07_periodo_pc_devolvida import PeriodoPcDevolvidaValidator

from .conftest import make_ctx


def _roda_legado(despesa, nova_data_transacao):
    try:
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=despesa,
            data_transacao=nova_data_transacao,
            rateios=[],
            despesas_impostos=[],
            recurso=despesa.recurso,
        )
    except serializers.ValidationError as exc:
        return exc
    return None


def _roda_pipeline(despesa, nova_data_transacao):
    ctx = make_ctx(despesa_instance=despesa, data_transacao=nova_data_transacao)
    try:
        PeriodoPcDevolvidaValidator().validate(ctx)
    except DespesaValidationError as exc:
        return exc
    return None


@pytest.mark.django_db
def test_paridade_data_fora_do_periodo_da_devolucao(
    despesa_factory, prestacao_conta_factory, associacao, periodo_2020_1, periodo_2020_2
):
    """Com PC devolvida no período 2020_2, mover a data_transacao para fora desse período (para o
    período 2020_1) deve ser invalidado em ambos os caminhos.
    """
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
    )
    prestacao_conta_factory(status=PrestacaoConta.STATUS_DEVOLVIDA, periodo=periodo_2020_2, associacao=associacao)
    nova_data = periodo_2020_1.data_inicio_realizacao_despesas + datetime.timedelta(days=3)

    erro_legado = _roda_legado(despesa, nova_data)
    erro_pipeline = _roda_pipeline(despesa, nova_data)
    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_data_dentro_do_periodo_da_devolucao(despesa_factory, prestacao_conta_factory, associacao, periodo_2020_2):  # noqa: E501
    """Manter a data_transacao dentro do mesmo período da PC devolvida deve ser aceito em ambos os caminhos."""
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
    )
    prestacao_conta_factory(status=PrestacaoConta.STATUS_DEVOLVIDA, periodo=periodo_2020_2, associacao=associacao)
    nova_data = periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=5)

    erro_legado = _roda_legado(despesa, nova_data)
    erro_pipeline = _roda_pipeline(despesa, nova_data)
    assert erro_legado is None
    assert erro_pipeline is None


@pytest.mark.django_db
def test_paridade_pc_nao_devolvida_nao_valida(despesa_factory, prestacao_conta_factory, associacao, periodo_2020_1, periodo_2020_2):  # noqa: E501
    """Sem PC no status DEVOLVIDA a regra é ignorada, mesmo movendo a data para outro período."""
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
    )
    prestacao_conta_factory(status=PrestacaoConta.STATUS_EM_ANALISE, periodo=periodo_2020_2, associacao=associacao)
    nova_data = periodo_2020_1.data_inicio_realizacao_despesas + datetime.timedelta(days=3)

    erro_legado = _roda_legado(despesa, nova_data)
    erro_pipeline = _roda_pipeline(despesa, nova_data)
    assert erro_legado is None
    assert erro_pipeline is None
