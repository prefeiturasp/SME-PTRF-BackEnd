from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class RateiosObrigatoriosValidator(AbstractDespesaValidator):
    """REG-002 — A despesa deve conter ao menos um rateio.

    Legado: validacao_despesa_service.py:45-48
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — exige ao menos um rateio associado à despesa.

        Levanta DespesaValidationError com detail={"rateios": [...]} quando ctx.rateios estiver vazio.
        """
        # validacao_despesa_service.py:45-48
        if not ctx.rateios:
            raise DespesaValidationError({
                "rateios": ["A despesa deve conter ao menos um rateio."],
                "validator": self.__class__.__name__
            })
        return ctx
