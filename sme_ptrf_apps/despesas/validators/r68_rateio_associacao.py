from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


class RateioAssociacaoValidator(AbstractDespesaValidator):
    """REG-068 — Cada rateio herda a associação da despesa.

    Associação enviada no payload do rateio é ignorada; o service legado já
    sobrescrevia `rateio["associacao"] = despesa.associacao` no create/update.

    Legado: despesa_service.py → `_criar_rateios` / `_atualizar_rateios`
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — sem checagem; a regra só normaliza dados na fase apply."""
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 2 — força `associacao` da despesa em todos os rateios.

        Mutação in-place nos dicts de `ctx.rateios` (mesma referência de
        `validated_data["rateios"]`), então propaga automaticamente ao payload.
        """
        for rateio in ctx.rateios:
            rateio["associacao"] = ctx.associacao
        return ctx
