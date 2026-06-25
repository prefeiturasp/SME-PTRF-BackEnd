from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class PagamentoAntecipadoValidator(AbstractDespesaValidator):
    """R14 — Pagamento antecipado (data_transacao < data_documento) exige motivos informados.
    R15 — Quando não há antecipação (dt >= dd), os motivos são descartados.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        dt = ctx.data_transacao
        dd = ctx.data_documento

        if not (dt and dd):
            return ctx

        if dt < dd and not ctx.motivos_pagamento_antecipado and not ctx.outros_motivos:
            raise DespesaValidationError({
                "detail": (
                    "Quando a Data da transação for menor que a Data do Documento "
                    "é necessário informar os motivos do pagamento antecipado."
                )
            })

        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """R15 — Descarta motivos de pagamento antecipado quando não há antecipação."""
        dt = ctx.data_transacao
        dd = ctx.data_documento

        if dt and dd and dt >= dd:
            ctx.motivos_pagamento_antecipado = []
            ctx.outros_motivos = ""

        return ctx
