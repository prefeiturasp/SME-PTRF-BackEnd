from sme_ptrf_apps.core.models import Periodo

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class PeriodoPcDevolvidaValidator(AbstractDespesaValidator):
    """R07 — Quando há PC devolvida para acertos, a data da despesa deve estar no período da devolução.

    Também resolve e injeta `ctx.periodo` para uso por validators posteriores (ex: v13_saldos).
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.data_transacao:
            return ctx

        recurso = ctx.recurso_efetivo
        if not recurso:
            return ctx

        periodo = Periodo.da_data_por_recurso(ctx.data_transacao, recurso)
        ctx.periodo = periodo

        instance = ctx.despesa_instance
        if not instance:
            return ctx

        pc = getattr(instance, "prestacao_conta", None)
        if not pc:
            return ctx

        if (
            pc.devolvida_para_acertos
            and periodo
            and periodo.referencia != pc.periodo.referencia
        ):
            raise DespesaValidationError({
                "mensagem": "Permitido apenas datas dentro do período referente à devolução."
            })

        return ctx
