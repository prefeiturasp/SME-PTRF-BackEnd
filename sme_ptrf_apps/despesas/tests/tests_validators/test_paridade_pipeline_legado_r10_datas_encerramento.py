"""Paridade REG-010: DespesaService._validar_datas (legado) vs DatasEncerramentoValidator."""
import datetime
from types import SimpleNamespace

import pytest
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r10_datas_encerramento import DatasEncerramentoValidator

from .conftest import make_ctx


def _associacao(data_de_encerramento):
    return SimpleNamespace(data_de_encerramento=data_de_encerramento)


def _roda_legado(associacao, data_documento, data_transacao):
    try:
        DespesaService._validar_datas({
            "associacao": associacao,
            "data_documento": data_documento,
            "data_transacao": data_transacao,
        })
    except serializers.ValidationError as exc:
        return exc
    return None


def _roda_pipeline(associacao, data_documento, data_transacao):
    ctx = make_ctx(associacao=associacao, data_documento=data_documento, data_transacao=data_transacao)
    try:
        DatasEncerramentoValidator().validate(ctx)
    except DespesaValidationError as exc:
        return exc
    return None


@pytest.mark.parametrize("campo_futuro", ["data_documento", "data_transacao"])
def test_paridade_data_posterior_ao_encerramento(campo_futuro):
    """data_documento ou data_transacao posterior à data_de_encerramento da associação deve ser
    invalidada em ambos os caminhos.
    """
    encerramento = datetime.date(2026, 1, 31)
    depois = datetime.date(2026, 2, 1)
    associacao = _associacao(encerramento)
    datas = {"data_documento": None, "data_transacao": None, campo_futuro: depois}

    erro_legado = _roda_legado(associacao, datas["data_documento"], datas["data_transacao"])
    erro_pipeline = _roda_pipeline(associacao, datas["data_documento"], datas["data_transacao"])
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_datas_dentro_do_prazo():
    """Ambas as datas anteriores à data_de_encerramento devem ser aceitas em ambos os caminhos."""
    associacao = _associacao(datetime.date(2026, 12, 31))
    data = datetime.date(2026, 1, 15)
    assert _roda_legado(associacao, data, data) is None
    assert _roda_pipeline(associacao, data, data) is None


def test_paridade_associacao_sem_data_de_encerramento():
    """Associação sem data_de_encerramento definida ignora a regra, mesmo com datas futuras."""
    associacao = _associacao(None)
    data = datetime.date(2099, 1, 1)
    assert _roda_legado(associacao, data, data) is None
    assert _roda_pipeline(associacao, data, data) is None
