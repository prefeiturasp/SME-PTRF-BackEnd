from datetime import date

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class DatasFuturasValidator(AbstractDespesaValidator):
    """REG-015 — Data de documento/pagamento não pode ser posterior a hoje.

    Hoje a regra vive no front (`validateFormDespesas`). Na pipeline, vira
    defesa no back com as mesmas mensagens.

    Legado (front): CadastroForm.js → validateFormDespesas
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — data_documento e data_transacao não podem ser > date.today().

        Levanta DespesaValidationError com detail no campo correspondente.
        Datas ausentes são ignoradas.
        """
        hoje = date.today()
        errors = {}

        if ctx.data_documento and ctx.data_documento > hoje:
            errors["data_documento"] = (
                "Data do documento não pode ser maior que a data de hoje"
            )

        if ctx.data_transacao and ctx.data_transacao > hoje:
            errors["data_transacao"] = (
                "Data do pagamento não pode ser maior que a data de hoje"
            )

        if errors:
            errors["validator"] = self.__class__.__name__
            raise DespesaValidationError(errors)

        return ctx
