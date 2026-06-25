from decimal import Decimal

from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ValorOriginalCapitalValidator(AbstractDespesaValidator):
    """R06b — valor_original do rateio CAPITAL deve ser igual a quantidade x valor_item.

    O campo valor_original é o valor exibido no extrato comprobatório; no fluxo de
    capital ele é calculado (disabled no frontend) e deve coincidir com valor_rateio.

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
            valor_original_rateio = Decimal(str(rateio.get("valor_original", 0)))
            valor_calculado = Decimal(str(valor_item)) * Decimal(str(quantidade))

            if valor_calculado != valor_original_rateio:
                raise DespesaValidationError({
                    "mensagem": "Valor total do capital diverge do valor calculado pela quantidade de itens"
                })

        return ctx