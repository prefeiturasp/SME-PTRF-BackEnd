from .base import AbstractDespesaValidator
from .context import DespesaDtoContext


class DataDocumentoVaziaValidator(AbstractDespesaValidator):
    """REG-028 — Data do documento vazia herda a data da transação.

    Na despesa principal: só copia se data_documento estiver vazia.
    Nos impostos: sempre alinha data_documento à data_transacao do imposto
    (equivalente a Despesa.verifica_data_documento_vazio / e_despesa_de_imposto).

    Legado: despesa.py → verifica_data_documento_vazio
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if ctx.data_transacao and not ctx.data_documento:
            ctx.data_documento = ctx.data_transacao

        for imposto in ctx.despesas_impostos:
            if not isinstance(imposto, dict):
                continue
            dt = imposto.get("data_transacao")
            if dt:
                imposto["data_documento"] = dt

        return ctx
