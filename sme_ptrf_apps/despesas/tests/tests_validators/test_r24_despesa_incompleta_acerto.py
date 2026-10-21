"""Testes REG-024 — despesa incompleta bloqueada em fluxo de acerto."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from sme_ptrf_apps.despesas.validators.base import DespesaValidationError
from sme_ptrf_apps.despesas.validators.r24_despesa_incompleta_acerto import (
    DespesaIncompletaAcertoValidator,
    MSG_INCOMPLETA_ACERTO,
)
from sme_ptrf_apps.despesas.tests.tests_validators.conftest import make_ctx


pytestmark = pytest.mark.django_db


def _tipo_doc(numero_digitado=False):
    return SimpleNamespace(numero_documento_digitado=numero_digitado)


def _tipo_transacao(tem_documento=False):
    return SimpleNamespace(tem_documento=tem_documento)


def _rateio_completo(**kwargs):
    base = {
        "conta_associacao": object(),
        "acao_associacao": object(),
        "aplicacao_recurso": "CUSTEIO",
        "valor_rateio": Decimal("100.00"),
        "tipo_custeio": object(),
        "especificacao_material_servico": object(),
        "saida_de_recurso_externo": False,
        "eh_despesa_sem_comprovacao_fiscal": False,
    }
    base.update(kwargs)
    return base


def _ctx_completo(**kwargs):
    defaults = dict(
        is_create=True,
        uuid_solicitacao_acerto="acerto-uuid",
        valor_total=Decimal("100.00"),
        data_transacao=date(2020, 3, 10),
        data_documento=date(2020, 3, 10),
        cpf_cnpj_fornecedor="11478276000104",
        nome_fornecedor="Fornecedor SA",
        tipo_documento=_tipo_doc(),
        tipo_transacao=_tipo_transacao(),
        numero_documento="123",
        documento_transacao="",
        rateios=[_rateio_completo()],
    )
    defaults.update(kwargs)
    return make_ctx(**defaults)


def test_acerto_permite_despesa_completa():
    ctx = _ctx_completo()
    result = DespesaIncompletaAcertoValidator().validate(ctx)
    assert result is ctx


def test_acerto_bloqueia_sem_data_transacao():
    ctx = _ctx_completo(data_transacao=None)
    with pytest.raises(DespesaValidationError) as exc:
        DespesaIncompletaAcertoValidator().validate(ctx)
    assert MSG_INCOMPLETA_ACERTO in str(exc.value.detail)


def test_acerto_bloqueia_rateio_incompleto():
    ctx = _ctx_completo(rateios=[{
        "conta_associacao": None,
        "acao_associacao": object(),
        "aplicacao_recurso": "CUSTEIO",
        "valor_rateio": Decimal("100.00"),
    }])
    with pytest.raises(DespesaValidationError):
        DespesaIncompletaAcertoValidator().validate(ctx)


def test_acerto_bloqueia_boletim_vazio_quando_nao_reconhecida():
    ctx = _ctx_completo(
        eh_despesa_reconhecida_pela_associacao=False,
        numero_boletim_de_ocorrencia="",
    )
    with pytest.raises(DespesaValidationError):
        DespesaIncompletaAcertoValidator().validate(ctx)
