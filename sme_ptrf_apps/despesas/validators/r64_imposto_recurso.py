from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


class ImpostoRecursoValidator(AbstractDespesaValidator):
    """REG-064 — Imposto novo herda o recurso da despesa geradora.

    Só aplica em impostos sem uuid (create). Imposto já persistido no update
    não re-copia o recurso.

    Legado: despesa_service.py → _processar_impostos
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.retem_imposto:
            return ctx

        recurso = ctx.recurso_efetivo
        if not recurso:
            return ctx

        for imposto in ctx.despesas_impostos:
            if not isinstance(imposto, dict):
                continue
            if imposto.get("uuid"):
                continue
            imposto["recurso"] = recurso

        return ctx
