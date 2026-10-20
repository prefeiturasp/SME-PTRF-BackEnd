from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class QuantidadeCapitalValidator(AbstractDespesaValidator):
    """REG-005 — Rateio CAPITAL deve ter quantidade_itens_capital > 0.

    Pré-condição obrigatória para REG-006: deve sempre preceder
    ValorOriginalCapitalValidator no pipeline.

    Legado: validacao_despesa_service.py:99-118
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — quantidade_itens_capital deve ser > 0 em todos os rateios CAPITAL.

        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro rateio inválido.
        Rateios não-CAPITAL são ignorados.
        """
        for rateio in ctx.rateios:
            # validacao_despesa_service.py:100-101
            if rateio.get("aplicacao_recurso") != APLICACAO_CAPITAL:
                continue

            # validacao_despesa_service.py:104-106 — or 0 evita TypeError quando None
            quantidade_itens_capital = rateio.get("quantidade_itens_capital") or 0

            # validacao_despesa_service.py:112-118
            if quantidade_itens_capital <= 0:
                raise DespesaValidationError({
                    "mensagem": "Rateio de capital não pode ter quantidade menor ou igual a zero",
                    "validator": self.__class__.__name__
                })

        return ctx
