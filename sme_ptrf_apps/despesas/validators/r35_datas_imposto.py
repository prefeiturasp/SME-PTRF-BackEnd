from datetime import date

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class DatasImpostoValidator(AbstractDespesaValidator):
    """REG-035 — Datas do imposto em relação à despesa principal.

    - Imposto com data exige data de pagamento na despesa principal.
    - Data do imposto não pode ser anterior à data da despesa.
    - Data do imposto não pode ser futura (maxDate = hoje no front).

    Ignorado quando não há retenção.

    Legado (front): CadastroForm.js → validacoesPersonalizadas
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.retem_imposto:
            return ctx

        hoje = date.today()
        data_despesa = ctx.data_transacao

        for imposto in ctx.despesas_impostos:
            if not isinstance(imposto, dict):
                continue

            data_imposto = imposto.get("data_transacao")
            if not data_imposto:
                continue

            if not data_despesa:
                raise DespesaValidationError({
                    "despesa_imposto_data_transacao": (
                        "Data do imposto sem data de despesa"
                    ),
                    "validator": self.__class__.__name__,
                })

            if data_imposto < data_despesa:
                raise DespesaValidationError({
                    "despesa_imposto_data_transacao": (
                        "Data do imposto menor que data da despesa"
                    ),
                    "validator": self.__class__.__name__,
                })

            if data_imposto > hoje:
                raise DespesaValidationError({
                    "despesa_imposto_data_transacao": (
                        "Data do pagamento não pode ser maior que a data de hoje"
                    ),
                    "validator": self.__class__.__name__,
                })

        return ctx
