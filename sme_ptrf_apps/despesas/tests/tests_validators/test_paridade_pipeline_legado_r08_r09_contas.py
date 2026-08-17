"""Paridade REG-008/REG-009: ValidacaoDespesaService.validar_periodo_e_contas (legado, ainda
importável) vs ContasRateiosValidator/ContasImpostosValidator/ContaAcaoRecursoValidator.
"""
import datetime
from types import SimpleNamespace

import pytest
from model_bakery import baker
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.validacao_despesa_service import ValidacaoDespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r08_contas_impostos import ContasImpostosValidator
from sme_ptrf_apps.despesas.validators.r08_contas_rateios import ContasRateiosValidator
from sme_ptrf_apps.despesas.validators.r09_conta_acao_recurso import ContaAcaoRecursoValidator

from .conftest import make_ctx

_PIPELINE_VALIDATORS = [ContasRateiosValidator(), ContasImpostosValidator(), ContaAcaoRecursoValidator()]


def _roda_legado(data_transacao, rateios, despesas_impostos, recurso):
    try:
        ValidacaoDespesaService.validar_periodo_e_contas(
            instance=None,
            data_transacao=data_transacao,
            rateios=rateios,
            despesas_impostos=despesas_impostos,
            recurso=recurso,
        )
    except serializers.ValidationError as exc:
        return exc
    return None


def _roda_pipeline(data_transacao, rateios, despesas_impostos):
    ctx = make_ctx(data_transacao=data_transacao, rateios=rateios, despesas_impostos=despesas_impostos)
    try:
        for validator in _PIPELINE_VALIDATORS:
            ctx = validator.validate(ctx)
    except DespesaValidationError as exc:
        return exc
    return None


@pytest.mark.django_db
def test_paridade_conta_e_acao_recursos_diferentes(associacao):
    """Rateio com conta e ação de recursos diferentes deve ser invalidado em ambos os caminhos (REG-009)."""
    recurso_a = baker.make("Recurso")
    recurso_b = baker.make("Recurso")
    conta = baker.make("ContaAssociacao", associacao=associacao, tipo_conta__recurso=recurso_a)
    acao = baker.make("AcaoAssociacao", associacao=associacao, acao__recurso=recurso_b)
    rateios = [{"conta_associacao": conta, "acao_associacao": acao}]

    erro_legado = _roda_legado(None, rateios, [], recurso_a)
    erro_pipeline = _roda_pipeline(None, rateios, [])
    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_conta_e_acao_mesmo_recurso(associacao):
    """Rateio com conta e ação do mesmo recurso deve ser aceito em ambos os caminhos (REG-009)."""
    recurso = baker.make("Recurso")
    conta = baker.make("ContaAssociacao", associacao=associacao, tipo_conta__recurso=recurso)
    acao = baker.make("AcaoAssociacao", associacao=associacao, acao__recurso=recurso)
    rateios = [{"conta_associacao": conta, "acao_associacao": acao}]

    erro_legado = _roda_legado(None, rateios, [], recurso)
    erro_pipeline = _roda_pipeline(None, rateios, [])
    assert erro_legado is None
    assert erro_pipeline is None


def test_paridade_conta_com_data_inicio_posterior_a_transacao():
    """Conta do rateio com data_inicio posterior à data_transacao deve ser invalidada em ambos os
    caminhos (REG-008).
    """
    conta = SimpleNamespace(data_inicio=datetime.date(2026, 6, 1), data_encerramento=None)
    data_transacao = datetime.date(2026, 1, 1)
    rateios = [{"conta_associacao": conta, "acao_associacao": None}]

    erro_legado = _roda_legado(data_transacao, rateios, [], None)
    erro_pipeline = _roda_pipeline(data_transacao, rateios, [])
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_conta_com_data_encerramento_anterior_a_transacao():
    """Conta do rateio com data_encerramento anterior à data_transacao deve ser invalidada em ambos
    os caminhos (REG-008).
    """
    conta = SimpleNamespace(
        data_inicio=datetime.date(2020, 1, 1),
        data_encerramento=datetime.date(2026, 1, 1),
    )
    data_transacao = datetime.date(2026, 6, 1)
    rateios = [{"conta_associacao": conta, "acao_associacao": None}]

    erro_legado = _roda_legado(data_transacao, rateios, [], None)
    erro_pipeline = _roda_pipeline(data_transacao, rateios, [])
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_conta_do_imposto_fora_da_vigencia():
    """Mesma checagem de vigência de conta, agora para a conta dentro de um imposto (despesas_impostos),
    fora da vigência — deve ser invalidada em ambos os caminhos (REG-008).
    """
    conta = SimpleNamespace(data_inicio=datetime.date(2026, 6, 1), data_encerramento=None)
    despesas_impostos = [{
        "data_transacao": datetime.date(2026, 1, 1),
        "rateios": [{"conta_associacao": conta}],
    }]

    erro_legado = _roda_legado(None, [], despesas_impostos, None)
    erro_pipeline = _roda_pipeline(None, [], despesas_impostos)
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_conta_do_rateio_dentro_da_vigencia():
    """Conta do rateio com data_transacao dentro do intervalo [data_inicio, data_encerramento] deve
    ser aceita em ambos os caminhos (REG-008, caso de sucesso).
    """
    conta = SimpleNamespace(
        data_inicio=datetime.date(2020, 1, 1),
        data_encerramento=datetime.date(2027, 1, 1),
    )
    data_transacao = datetime.date(2026, 6, 1)
    rateios = [{"conta_associacao": conta, "acao_associacao": None}]

    erro_legado = _roda_legado(data_transacao, rateios, [], None)
    erro_pipeline = _roda_pipeline(data_transacao, rateios, [])
    assert erro_legado is None
    assert erro_pipeline is None


def test_paridade_conta_do_imposto_dentro_da_vigencia():
    """Mesmo caso de sucesso anterior, agora para a conta dentro de um imposto (despesas_impostos)
    (REG-008, caso de sucesso).
    """
    conta = SimpleNamespace(
        data_inicio=datetime.date(2020, 1, 1),
        data_encerramento=datetime.date(2027, 1, 1),
    )
    despesas_impostos = [{
        "data_transacao": datetime.date(2026, 6, 1),
        "rateios": [{"conta_associacao": conta}],
    }]

    erro_legado = _roda_legado(None, [], despesas_impostos, None)
    erro_pipeline = _roda_pipeline(None, [], despesas_impostos)
    assert erro_legado is None
    assert erro_pipeline is None
