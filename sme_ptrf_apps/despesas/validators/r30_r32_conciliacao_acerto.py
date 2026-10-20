"""REG-030 / REG-032 — Conciliação automática em fluxos de acerto (apply).

REG-030: create via acerto — todos os rateios nascem conciliados no período da análise.
REG-032: update via acerto — rateios novos herdam conciliação se os existentes estão conciliados.
"""
from sme_ptrf_apps.core.models.solicitacao_acerto_documento import SolicitacaoAcertoDocumento
from sme_ptrf_apps.despesas.services.fluxo_acerto import (
    obter_analise_lancamento_edicao_pendente,
)

from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj, key, value):
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def _periodo_da_solicitacao_documento(uuid_solicitacao_acerto):
    if not uuid_solicitacao_acerto:
        return None
    solicitacao = SolicitacaoAcertoDocumento.objects.filter(
        uuid=uuid_solicitacao_acerto
    ).select_related(
        "analise_documento__analise_prestacao_conta__prestacao_conta__periodo"
    ).first()
    if not solicitacao:
        return None
    try:
        return (
            solicitacao.analise_documento
            .analise_prestacao_conta
            .prestacao_conta
            .periodo
        )
    except AttributeError:
        return None


def _periodo_da_analise_lancamento(despesa):
    analise = obter_analise_lancamento_edicao_pendente(despesa)
    if not analise:
        return None
    try:
        return analise.analise_prestacao_conta.prestacao_conta.periodo
    except AttributeError:
        return None


def _conciliar_rateio(rateio, periodo):
    _set(rateio, "update_conferido", True)
    _set(rateio, "conferido", True)
    _set(rateio, "periodo_conciliacao", periodo)


class ConciliacaoAcertoValidator(AbstractDespesaValidator):
    """REG-030 (create) e REG-032 (update) — apply only."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.is_acerto:
            return ctx

        if ctx.is_create:
            periodo = _periodo_da_solicitacao_documento(ctx.uuid_solicitacao_acerto)
            if not periodo:
                return ctx
            for rateio in ctx.rateios:
                _conciliar_rateio(rateio, periodo)
            return ctx

        # update — REG-032
        periodo = _periodo_da_analise_lancamento(ctx.despesa_instance)
        if not periodo:
            return ctx

        existentes = [r for r in ctx.rateios if _get(r, "uuid") or _get(r, "id")]
        novos = [r for r in ctx.rateios if not _get(r, "uuid") and not _get(r, "id")]
        if not novos:
            return ctx

        nao_conciliados = [
            r for r in existentes if not bool(_get(r, "conferido"))
        ]
        if nao_conciliados:
            return ctx

        for rateio in novos:
            _conciliar_rateio(rateio, periodo)

        return ctx
