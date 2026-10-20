from decimal import Decimal

from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ValorOriginalCapitalValidator(AbstractDespesaValidator):
    """REG-006 — valor_original do rateio CAPITAL deve ser igual a quantidade x valor_item.

    O campo valor_original é calculado (disabled no frontend) e deve coincidir com
    o produto quantidade_itens_capital * valor_item_capital.

    Depende de REG-005 (QuantidadeCapitalValidator) ter passado antes — a quantidade
    já é garantidamente positiva neste ponto.

    Legado: validacao_despesa_service.py:99-143
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — valor_original do rateio CAPITAL deve igualar quantidade_itens_capital × valor_item_capital.

        Rateios sem valor_item_capital são ignorados.
        Levanta DespesaValidationError com detail={"mensagem": "..."} quando há divergência.
        """
        for rateio in ctx.rateios:
            # validacao_despesa_service.py:100-101
            if rateio.get("aplicacao_recurso") != APLICACAO_CAPITAL:
                continue

            # validacao_despesa_service.py:104-110
            quantidade_itens_capital = rateio.get("quantidade_itens_capital") or 0
            valor_item_capital = rateio.get("valor_item_capital")

            # validacao_despesa_service.py:120-121
            if not valor_item_capital:
                continue

            # validacao_despesa_service.py:123-130
            valor_total_item_capital = (
                Decimal(str(valor_item_capital)) * Decimal(str(quantidade_itens_capital))
            )
            valor_original_rateio = Decimal(str(rateio.get("valor_original", 0)))

            # validacao_despesa_service.py:137-143
            if valor_total_item_capital != valor_original_rateio:
                raise DespesaValidationError({
                    "mensagem": "Valor total do capital diverge do valor calculado pela quantidade de itens",
                    "validator": self.__class__.__name__
                })

        return ctx
