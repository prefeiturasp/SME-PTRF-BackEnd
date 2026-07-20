from decimal import Decimal

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class SomaValorOriginalValidator(AbstractDespesaValidator):
    """R04b — Soma de valor_original dos rateios deve igualar o valor_original real da despesa.

    Executa mesmo quando valor_original é None — nesse caso trata como 0, igual ao legado
    (ValidacaoDespesaService.validar_rateios_serializer).

    Legado: validacao_despesa_service.py:55-97
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — soma de valor_original dos rateios (+ impostos) deve igualar valor_original_real_despesa.

        Levanta DespesaValidationError com detail={"rateios": "mensagem"} quando há divergência.
        Trata ctx.valor_original=None como 0, idêntico ao legado.
        """
        # validacao_despesa_service.py:55-58
        total_rateios_original = sum(
            Decimal(str(r.get("valor_original", 0))) for r in ctx.rateios
        )

        # validacao_despesa_service.py:65-68 — valor_original or 0 quando None
        valor_original_real_despesa = (
            Decimal(str(ctx.valor_original or 0)) - ctx.valor_recursos_proprios
        )
        total_rateios_original_com_impostos = total_rateios_original

        # validacao_despesa_service.py:73-85
        if ctx.retem_imposto:
            total_impostos_valor_original = sum(
                Decimal(str(imp.get("valor_original", 0))) for imp in ctx.despesas_impostos
            )
            total_rateios_original_com_impostos += total_impostos_valor_original

        # validacao_despesa_service.py:93-97
        if total_rateios_original_com_impostos != valor_original_real_despesa:
            raise DespesaValidationError({
                "rateios": "A soma dos valores originais dos rateios deve ser igual ao valor original da despesa.",
                "validator": self.__class__.__name__
            })

        return ctx
