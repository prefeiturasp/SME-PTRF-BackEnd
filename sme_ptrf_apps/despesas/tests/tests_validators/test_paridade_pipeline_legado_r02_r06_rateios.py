"""Paridade REG-002 a REG-006: ValidacaoDespesaService.validar_rateios_serializer
(legado, ainda importável) vs os validators correspondentes na pipeline.
"""
from decimal import Decimal

import pytest
from rest_framework import serializers

from sme_ptrf_apps.despesas.services.validacao_despesa_service import ValidacaoDespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r02_rateios_obrigatorios import RateiosObrigatoriosValidator
from sme_ptrf_apps.despesas.validators.r03_soma_valor_rateio import SomaValorRateioValidator
from sme_ptrf_apps.despesas.validators.r04_soma_valor_original import SomaValorOriginalValidator
from sme_ptrf_apps.despesas.validators.r05_quantidade_capital import QuantidadeCapitalValidator
from sme_ptrf_apps.despesas.validators.r06_valor_original_capital import ValorOriginalCapitalValidator

from .conftest import make_ctx

CAPITAL = "CAPITAL"
CUSTEIO = "CUSTEIO"

_PIPELINE_VALIDATORS = [
    RateiosObrigatoriosValidator(),
    SomaValorRateioValidator(),
    SomaValorOriginalValidator(),
    QuantidadeCapitalValidator(),
    ValorOriginalCapitalValidator(),
]


def _roda_legado(**kwargs):
    try:
        ValidacaoDespesaService.validar_rateios_serializer(**kwargs)
    except serializers.ValidationError as exc:
        return exc
    return None


def _roda_pipeline(**kwargs):
    ctx = make_ctx(
        valor_total=Decimal(str(kwargs.get("valor_total") or 0)),
        valor_original=Decimal(str(kwargs.get("valor_original") or 0)),
        valor_recursos_proprios=Decimal(str(kwargs.get("valor_recursos_proprios") or 0)),
        retem_imposto=kwargs.get("retem_imposto", False),
        rateios=kwargs.get("raw_rateios") or [],
        despesas_impostos=kwargs.get("raw_despesas_impostos") or [],
    )
    try:
        for validator in _PIPELINE_VALIDATORS:
            ctx = validator.validate(ctx)
    except DespesaValidationError as exc:
        return exc
    return None


@pytest.mark.parametrize("kwargs", [
    dict(valor_total=100, valor_original=100, raw_rateios=[]),
    dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{"valor_rateio": 50, "valor_original": 100, "aplicacao_recurso": CUSTEIO}],
    ),
    dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{"valor_rateio": 100, "valor_original": 50, "aplicacao_recurso": CUSTEIO}],
    ),
    dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{
            "valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CAPITAL,
            "quantidade_itens_capital": 0, "valor_item_capital": 100,
        }],
    ),
    dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{
            "valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CAPITAL,
            "quantidade_itens_capital": 2, "valor_item_capital": 30,
        }],
    ),
])
def test_paridade_casos_de_erro(kwargs):
    """Cada variação de kwargs cobre um caso inválido diferente (sem rateio, soma de valor_rateio
    divergente do total, soma de valor_original divergente, capital sem quantidade de itens,
    capital com valor de item incompatível) — ambos os caminhos devem rejeitar.
    """
    erro_legado = _roda_legado(**kwargs)
    erro_pipeline = _roda_pipeline(**kwargs)
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_custeio_valido():
    """Rateio único em CUSTEIO com somas batendo deve ser aceito em ambos os caminhos."""
    kwargs = dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{"valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CUSTEIO}],
    )
    assert _roda_legado(**kwargs) is None
    assert _roda_pipeline(**kwargs) is None


def test_paridade_capital_valido():
    """Rateio único em CAPITAL com quantidade/valor de itens consistentes com o valor_rateio deve
    ser aceito em ambos os caminhos.
    """
    kwargs = dict(
        valor_total=100, valor_original=100,
        raw_rateios=[{
            "valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CAPITAL,
            "quantidade_itens_capital": 2, "valor_item_capital": 50,
        }],
    )
    assert _roda_legado(**kwargs) is None
    assert _roda_pipeline(**kwargs) is None


def test_paridade_com_imposto_retido_valido():
    """Com retem_imposto=True, o valor do imposto deve compor a soma total junto do rateio; quando
    a soma bate, ambos os caminhos aceitam.
    """
    kwargs = dict(
        valor_total=150, valor_original=150, retem_imposto=True,
        raw_rateios=[{"valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CUSTEIO}],
        raw_despesas_impostos=[{"valor_total": 50, "valor_original": 50}],
    )
    assert _roda_legado(**kwargs) is None
    assert _roda_pipeline(**kwargs) is None


def test_paridade_com_imposto_retido_soma_invalida():
    """Mesmo cenário anterior, mas com o valor do imposto divergente do necessário para fechar a
    soma total — ambos os caminhos devem rejeitar.
    """
    kwargs = dict(
        valor_total=150, valor_original=150, retem_imposto=True,
        raw_rateios=[{"valor_rateio": 100, "valor_original": 100, "aplicacao_recurso": CUSTEIO}],
        raw_despesas_impostos=[{"valor_total": 30, "valor_original": 30}],
    )
    assert _roda_legado(**kwargs) is not None
    assert _roda_pipeline(**kwargs) is not None
