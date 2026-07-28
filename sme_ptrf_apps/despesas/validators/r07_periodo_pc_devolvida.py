from sme_ptrf_apps.core.models import Periodo

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class PeriodoPcDevolvidaValidator(AbstractDespesaValidator):
    """REG-007 — Quando há PC devolvida para acertos, a data da despesa deve estar no período da devolução.

    Também resolve e injeta ctx.periodo para uso por validators posteriores (ex: SaldosValidator).

    Legado: validacao_despesa_service.py:154-167
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — valida que a data está dentro do período da PC devolvida para acertos.

        Injeta ctx.periodo como efeito colateral para uso por validators posteriores.
        Levanta DespesaValidationError com detail={"mensagem": "..."} quando a data está fora do período.
        Ignorado quando data_transacao, recurso ou PC ausentes.
        """
        # validacao_despesa_service.py:154
        if not ctx.data_transacao:
            return ctx

        recurso = ctx.recurso_efetivo
        if not recurso:
            return ctx

        # validacao_despesa_service.py:155
        periodo = Periodo.da_data_por_recurso(ctx.data_transacao, recurso)
        ctx.periodo = periodo

        instance = ctx.despesa_instance
        if not instance:
            return ctx

        pc = getattr(instance, "prestacao_conta", None)
        if not pc:
            return ctx

        # validacao_despesa_service.py:157-167
        if pc.devolvida_para_acertos and periodo and periodo.referencia != pc.periodo.referencia:
            raise DespesaValidationError({
                "mensagem": "Permitido apenas datas dentro do período referente à devolução.",
                "validator": self.__class__.__name__
            })

        return ctx
