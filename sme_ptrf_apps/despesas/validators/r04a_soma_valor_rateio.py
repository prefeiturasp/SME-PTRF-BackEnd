from decimal import Decimal

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class SomaValorRateioValidator(AbstractDespesaValidator):
    """R04a — Soma de valor_rateio dos rateios deve igualar o valor real da despesa.

    valor_total_real_despesa = valor_total - valor_recursos_proprios
    Se retem_imposto=True, inclui a soma de valor_total das despesas de imposto.

    Legado: validacao_despesa_service.py:50-91
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — soma de valor_rateio dos rateios (+ impostos) deve igualar valor_total_real_despesa.

        Levanta DespesaValidationError com detail={"rateios": "mensagem"} quando há divergência.
        """
        # validacao_despesa_service.py:50-53
        total_rateios = sum(
            Decimal(str(r.get("valor_rateio", 0))) for r in ctx.rateios
        )

        # validacao_despesa_service.py:60-63
        valor_total_real_despesa = ctx.valor_total - ctx.valor_recursos_proprios
        total_rateios_com_impostos = total_rateios

        # validacao_despesa_service.py:73-85
        if ctx.retem_imposto:
            total_impostos_valor_total = sum(
                Decimal(str(imp.get("valor_total", 0))) for imp in ctx.despesas_impostos
            )
            total_rateios_com_impostos += total_impostos_valor_total

        # validacao_despesa_service.py:87-91
        if total_rateios_com_impostos != valor_total_real_despesa:
            raise DespesaValidationError({
                "rateios": "A soma dos valores realizados dos rateios deve ser igual ao valor real da despesa.",
                "validator": self.__class__.__name__
            })

        return ctx
