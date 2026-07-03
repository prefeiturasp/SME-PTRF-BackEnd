from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContaAcaoRecursoValidator(AbstractDespesaValidator):
    """R12 — Conta e Ação de cada rateio devem pertencer ao mesmo recurso.

    Legado: validacao_despesa_service.py:177-183
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — conta_associacao e acao_associacao de cada rateio devem ser do mesmo recurso.

        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro rateio com divergência.
        Rateios sem conta_associacao ou acao_associacao são ignorados.
        """
        for rateio in ctx.rateios:
            # validacao_despesa_service.py:178-179
            conta_associacao = rateio.get("conta_associacao")
            acao_associacao = rateio.get("acao_associacao")

            # validacao_despesa_service.py:181-183
            if conta_associacao and acao_associacao:
                recurso_conta = getattr(getattr(conta_associacao, "tipo_conta", None), "recurso", None)
                recurso_acao = getattr(getattr(acao_associacao, "acao", None), "recurso", None)

                if recurso_conta and recurso_acao and recurso_conta != recurso_acao:
                    raise DespesaValidationError({
                        "mensagem": "Conta e Ação devem ser do mesmo recurso.",
                        "validator": self.__class__.__name__
                    })

        return ctx
