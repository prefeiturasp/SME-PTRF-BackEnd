from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ImpostosValidator(AbstractDespesaValidator):
    """R16 — Cada despesa de imposto deve ter ao menos um rateio associado."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.retem_imposto:
            return ctx

        for imposto in ctx.despesas_impostos:
            rateios = imposto.get("rateios", [])
            if not rateios:
                raise DespesaValidationError({
                    "mensagem": "A despesa de imposto precisa ter rateio associado"
                })

        return ctx
