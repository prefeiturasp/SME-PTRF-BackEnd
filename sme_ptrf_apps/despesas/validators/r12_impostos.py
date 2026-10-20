from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ImpostosValidator(AbstractDespesaValidator):
    """REG-012 — Cada despesa de imposto deve ter ao menos um rateio associado.

    Legado: despesa_service.py:399-403 (_processar_impostos)
             despesa_service.py:434-438 (_processar_impostos_update)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — cada despesa de imposto deve possuir ao menos um rateio.

        Ignorado quando ctx.retem_imposto é False.
        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro imposto sem rateio.
        """
        # despesa_service.py:390-403
        if ctx.retem_imposto:
            self._validar_rateios_dos_impostos(ctx.despesas_impostos)
        return ctx

    @staticmethod
    def _validar_rateios_dos_impostos(despesas_impostos: list) -> None:
        """Levanta DespesaValidationError quando algum imposto não possui rateios."""
        for imposto in despesas_impostos:
            rateios = imposto.get("rateios", [])
            if not rateios:
                raise DespesaValidationError({
                    "mensagem": "A despesa de imposto precisa ter rateio associado",
                    "validator": "ImpostosValidator"
                })
