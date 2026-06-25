from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class RateiosObrigatoriosValidator(AbstractDespesaValidator):
    """R01 — A despesa deve conter ao menos um rateio."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.rateios:
            raise DespesaValidationError("A despesa deve conter ao menos um rateio.")
        return ctx
