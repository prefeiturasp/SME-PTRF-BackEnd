"""Paridade REG-012: checagem de rateio obrigatório em despesas_impostos, embutida em
DespesaService._processar_impostos/_processar_impostos_update (legado, pipeline_ativa=False)
vs ImpostosValidator.
"""
import copy

import pytest
from model_bakery import baker
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r12_impostos import ImpostosValidator

from .conftest import make_ctx


def _roda_pipeline(retem_imposto, despesas_impostos):
    ctx = make_ctx(retem_imposto=retem_imposto, despesas_impostos=despesas_impostos)
    try:
        ImpostosValidator().validate(ctx)
    except DespesaValidationError as exc:
        return exc
    return None


@pytest.mark.django_db
def test_paridade_create_sem_rateio_no_imposto(associacao):
    """Imposto retido sem nenhum rateio deve ser invalidado tanto no create legado quanto na pipeline."""
    despesa = baker.make("Despesa", associacao=associacao, retem_imposto=True)
    despesas_impostos = [{"rateios": []}]

    try:
        DespesaService._processar_impostos(despesa, list(despesas_impostos), pipeline_ativa=False)
        erro_legado = None
    except serializers.ValidationError as exc:
        erro_legado = exc

    erro_pipeline = _roda_pipeline(True, despesas_impostos)

    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_update_sem_rateio_no_imposto(associacao):
    """Mesmo cenário de rateio ausente, agora no fluxo de update (_processar_impostos_update)."""
    despesa = baker.make("Despesa", associacao=associacao, retem_imposto=True)
    despesas_impostos = [{"rateios": []}]

    try:
        DespesaService._processar_impostos_update(despesa, list(despesas_impostos), pipeline_ativa=False)
        erro_legado = None
    except serializers.ValidationError as exc:
        erro_legado = exc

    erro_pipeline = _roda_pipeline(True, despesas_impostos)

    assert erro_legado is not None
    assert erro_pipeline is not None


@pytest.mark.django_db
def test_paridade_sem_retencao_de_imposto_nao_valida(associacao):
    """Sem retenção de imposto (retem_imposto=False) a regra é ignorada, mesmo com rateios vazios."""
    despesa = baker.make("Despesa", associacao=associacao, retem_imposto=False)
    despesas_impostos = [{"rateios": []}]

    DespesaService._processar_impostos(despesa, list(despesas_impostos), pipeline_ativa=False)
    erro_pipeline = _roda_pipeline(False, despesas_impostos)

    assert erro_pipeline is None


@pytest.mark.django_db
def test_paridade_create_com_rateio_no_imposto(associacao):
    """Caso de sucesso: imposto retido com rateio válido não deve gerar erro em nenhum caminho."""
    despesa = baker.make("Despesa", associacao=associacao, retem_imposto=True)
    despesas_impostos = [{"rateios": [{"valor_rateio": 100, "aplicacao_recurso": "CUSTEIO"}]}]

    DespesaService._processar_impostos(despesa, copy.deepcopy(despesas_impostos), pipeline_ativa=False)
    erro_pipeline = _roda_pipeline(True, copy.deepcopy(despesas_impostos))

    assert erro_pipeline is None
