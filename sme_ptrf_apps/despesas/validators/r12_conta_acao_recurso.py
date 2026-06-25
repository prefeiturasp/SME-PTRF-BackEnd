from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContaAcaoRecursoValidator(AbstractDespesaValidator):
    """R12 — Conta e Ação de cada rateio devem pertencer ao mesmo recurso."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        for rateio in ctx.rateios:
            conta = rateio.get("conta_associacao")
            acao = rateio.get("acao_associacao")

            if not (conta and acao):
                continue

            recurso_conta = getattr(getattr(conta, "tipo_conta", None), "recurso", None)
            recurso_acao = getattr(getattr(acao, "acao", None), "recurso", None)

            if recurso_conta and recurso_acao and recurso_conta != recurso_acao:
                raise DespesaValidationError({
                    "mensagem": "Conta e Ação devem ser do mesmo recurso."
                })

        return ctx
