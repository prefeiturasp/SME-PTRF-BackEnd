from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class TesteBlockValidator(AbstractDespesaValidator):
    """R00 — Validator exclusivo para testes de pipeline.

    Sempre levanta DespesaValidationError — não deve ser ativado em produção.
    Útil para verificar que o pipeline está sendo executado corretamente.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — sempre levanta erro de validação (uso exclusivo em testes)."""
        raise DespesaValidationError({
            "mensagem": "Teste de validate pipeline.",
            "validator": self.__class__.__name__
        })

