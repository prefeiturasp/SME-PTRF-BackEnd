from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class QuantidadeCapitalValidator(AbstractDespesaValidator):
    """R05 — Rateio CAPITAL deve ter quantidade_itens_capital > 0.

    Pré-condição obrigatória para R06a e R06b: deve sempre preceder
    ValorRateioCapitalValidator e ValorOriginalCapitalValidator no pipeline.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        for rateio in ctx.rateios:
            if rateio.get("aplicacao_recurso") != APLICACAO_CAPITAL:
                continue

            quantidade = rateio.get("quantidade_itens_capital") or 0

            if quantidade <= 0:
                raise DespesaValidationError({
                    "mensagem": "Rateio de capital não pode ter quantidade menor ou igual a zero"
                })

        return ctx
