"""Paridade REG-011: DespesaService._processar_pagamento_antecipado (legado, pipeline_ativa=False)
vs PagamentoAntecipadoValidator.
"""
import datetime

from rest_framework import serializers

from sme_ptrf_apps.despesas.services.despesa_service import DespesaService
from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r11_pagamento_antecipado import PagamentoAntecipadoValidator

from .conftest import make_ctx


def _roda_legado(motivos, outros, data_transacao, data_documento):
    validated_data = {
        "motivos_pagamento_antecipado": list(motivos),
        "outros_motivos_pagamento_antecipado": outros,
        "data_transacao": data_transacao,
        "data_documento": data_documento,
    }
    try:
        motivos_final, outros_final = DespesaService._processar_pagamento_antecipado(
            validated_data, pipeline_ativa=False
        )
    except serializers.ValidationError as exc:
        return exc, None, None
    return None, motivos_final, outros_final


def _roda_pipeline(motivos, outros, data_transacao, data_documento):
    ctx = make_ctx(
        motivos_pagamento_antecipado=list(motivos),
        outros_motivos=outros,
        data_transacao=data_transacao,
        data_documento=data_documento,
    )
    validator = PagamentoAntecipadoValidator()
    try:
        validator.validate(ctx)
    except DespesaValidationError as exc:
        return exc, None, None
    validator.apply(ctx)
    return None, ctx.motivos_pagamento_antecipado, ctx.outros_motivos


def test_paridade_antecipado_sem_motivo():
    """Pagamento antecipado (data_transacao < data_documento) sem motivo informado deve ser
    invalidado em ambos os caminhos.
    """
    dt = datetime.date(2026, 1, 5)
    dd = datetime.date(2026, 1, 10)
    erro_legado, _, _ = _roda_legado([], "", dt, dd)
    erro_pipeline, _, _ = _roda_pipeline([], "", dt, dd)
    assert erro_legado is not None
    assert erro_pipeline is not None


def test_paridade_antecipado_com_motivo():
    """Pagamento antecipado com motivo informado deve ser aceito e o motivo preservado em ambos
    os caminhos.
    """
    dt = datetime.date(2026, 1, 5)
    dd = datetime.date(2026, 1, 10)
    erro_legado, motivos_legado, outros_legado = _roda_legado(["motivo-x"], "", dt, dd)
    erro_pipeline, motivos_pipeline, outros_pipeline = _roda_pipeline(["motivo-x"], "", dt, dd)
    assert erro_legado is None
    assert erro_pipeline is None
    assert motivos_legado == motivos_pipeline == ["motivo-x"]
    assert outros_legado == outros_pipeline == ""


def test_paridade_nao_antecipado_reseta_motivos():
    """Quando não é pagamento antecipado (data_transacao >= data_documento), motivos e outros_motivos
    devem ser resetados/ignorados em ambos os caminhos, mesmo que informados.
    """
    dt = datetime.date(2026, 1, 10)
    dd = datetime.date(2026, 1, 5)
    erro_legado, motivos_legado, outros_legado = _roda_legado(["motivo-x"], "texto qualquer", dt, dd)
    erro_pipeline, motivos_pipeline, outros_pipeline = _roda_pipeline(["motivo-x"], "texto qualquer", dt, dd)
    assert erro_legado is None
    assert erro_pipeline is None
    assert motivos_legado == motivos_pipeline == []
    assert outros_legado == outros_pipeline == ""


def test_paridade_datas_iguais_nao_e_antecipado():
    """data_transacao igual a data_documento não caracteriza pagamento antecipado; motivos devem
    ser descartados em ambos os caminhos.
    """
    data = datetime.date(2026, 1, 10)
    erro_legado, motivos_legado, _ = _roda_legado(["motivo-x"], "", data, data)
    erro_pipeline, motivos_pipeline, _ = _roda_pipeline(["motivo-x"], "", data, data)
    assert erro_legado is None
    assert erro_pipeline is None
    assert motivos_legado == motivos_pipeline == []


def test_paridade_sem_data_nao_valida():
    """Sem data_transacao/data_documento definidas, a regra não é aplicada e os motivos informados
    são mantidos como estão em ambos os caminhos.
    """
    erro_legado, motivos_legado, _ = _roda_legado(["motivo-x"], "", None, None)
    erro_pipeline, motivos_pipeline, _ = _roda_pipeline(["motivo-x"], "", None, None)
    assert erro_legado is None
    assert erro_pipeline is None
    assert motivos_legado == motivos_pipeline == ["motivo-x"]
