"""REG-019 — Período fechado (fluxo normal: create/update sem acerto).

Espelha o front (`getPeriodoFechado` → `status-periodo`):
`aceita_alteracoes = False` quando já existe Prestação de Contas da associação
no período da data. Nos fluxos de acerto a regra não se aplica (vale REG-007).
"""
from sme_ptrf_apps.core.models import Periodo, PrestacaoConta

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_PERIODO_FECHADO = "Período Fechado"


def _periodo_bloqueado_para_data(data, associacao, recurso) -> bool:
    """True quando existe PC no período da data (mesmo critério de status-periodo)."""
    if not data or not associacao or not recurso:
        return False

    periodo = Periodo.da_data_por_recurso(data, recurso)
    if not periodo:
        return False

    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)
    return prestacao is not None


class PeriodoFechadoValidator(AbstractDespesaValidator):
    """REG-019 — Fluxos 1 e 2: bloqueia save quando o período da data já tem PC."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if ctx.is_acerto:
            return ctx

        recurso = ctx.recurso_efetivo
        associacao = ctx.associacao
        if not recurso or not associacao:
            return ctx

        if _periodo_bloqueado_para_data(ctx.data_transacao, associacao, recurso):
            raise DespesaValidationError({
                "data_transacao": MSG_PERIODO_FECHADO,
                "mensagem": MSG_PERIODO_FECHADO,
                "validator": self.__class__.__name__,
            })

        if ctx.retem_imposto:
            for index, imposto in enumerate(ctx.despesas_impostos or []):
                if not isinstance(imposto, dict):
                    continue
                data_imposto = imposto.get("data_transacao")
                if _periodo_bloqueado_para_data(data_imposto, associacao, recurso):
                    raise DespesaValidationError({
                        "despesa_imposto_data_transacao": MSG_PERIODO_FECHADO,
                        "mensagem": MSG_PERIODO_FECHADO,
                        "index_imposto": index,
                        "validator": self.__class__.__name__,
                    })

        return ctx
