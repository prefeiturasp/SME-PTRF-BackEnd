from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class RecursoObrigatorioValidator(AbstractDespesaValidator):
    """REG-001 — Recurso da despesa é obrigatório.

    Presente apenas em CREATE_PIPELINE e CREATE_ACERTO_PIPELINE (pipelines.py).

    Legado: despesa_serializer.py:111-117
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — exige que ctx.recurso esteja preenchido.

        Levanta DespesaValidationError com detail="string" quando recurso ausente.
        """
        # despesa_serializer.py:111-117
        if not ctx.recurso:
            raise DespesaValidationError({
                "mensagem": "Recurso da despesa é obrigatório",
                "validator": self.__class__.__name__
            })
        return ctx
