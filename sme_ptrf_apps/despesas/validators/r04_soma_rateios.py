from decimal import Decimal

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class SomaRateiosValidator(AbstractDespesaValidator):
    """R04a — Soma de valor_rateio deve igualar o valor real da despesa.
    R04b — Soma de valor_original dos rateios deve igualar o valor_original da despesa.

    valor_real = valor_total - valor_recursos_proprios
    Se retem_imposto=True, soma também os valor_total/valor_original das despesas de imposto.

    R04b só é executada quando ctx.valor_original está presente (campo opcional na despesa).
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        # R04a — valor_rateio
        total_rateios = sum(
            Decimal(str(r.get("valor_rateio", 0))) for r in ctx.rateios
        )

        valor_real = ctx.valor_total - ctx.valor_recursos_proprios
        total_com_impostos = total_rateios

        if ctx.retem_imposto:
            total_impostos = sum(
                Decimal(str(imp.get("valor_total", 0))) for imp in ctx.despesas_impostos
            )
            total_com_impostos += total_impostos

        if total_com_impostos != valor_real:
            raise DespesaValidationError(
                "A soma dos valores realizados dos rateios deve ser igual ao valor real da despesa."
            )

        # R04b — valor_original (apenas quando informado na despesa)
        if ctx.valor_original is not None:
            total_original = sum(
                Decimal(str(r.get("valor_original", 0))) for r in ctx.rateios
            )
            total_original_com_impostos = total_original

            if ctx.retem_imposto:
                total_impostos_original = sum(
                    Decimal(str(imp.get("valor_original", 0))) for imp in ctx.despesas_impostos
                )
                total_original_com_impostos += total_impostos_original

            if total_original_com_impostos != ctx.valor_original:
                raise DespesaValidationError(
                    "A soma dos valores originais dos rateios deve ser igual ao valor original da despesa."
                )

        return ctx
