from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class RecursoObrigatorioValidator(AbstractDespesaValidator):
    """R02 — Recurso da despesa é obrigatório."""

    applies_to_update = False

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.recurso:
            raise DespesaValidationError("Recurso da despesa é obrigatório")
        return ctx
