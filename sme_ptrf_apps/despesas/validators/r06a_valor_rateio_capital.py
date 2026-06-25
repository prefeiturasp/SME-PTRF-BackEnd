from decimal import Decimal

from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ValorRateioCapitalValidator(AbstractDespesaValidator):
    """R06a — valor_rateio do rateio CAPITAL deve ser igual a quantidade x valor_item.

    Depende de R05 (QuantidadeCapitalValidator) ter passado antes — a quantidade
    já é garantidamente positiva neste ponto.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        for rateio in ctx.rateios:
            if rateio.get("aplicacao_recurso") != APLICACAO_CAPITAL:
                continue

            valor_item = rateio.get("valor_item_capital")
            if not valor_item:
                continue

            quantidade = rateio.get("quantidade_itens_capital") or 0
            valor_rateio = Decimal(str(rateio.get("valor_rateio", 0)))
            valor_calculado = Decimal(str(valor_item)) * Decimal(str(quantidade))

            if valor_calculado != valor_rateio:
                raise DespesaValidationError({
                    "mensagem": "Valor do rateio capital diverge do valor calculado pela quantidade de itens"
                })

        return ctx
