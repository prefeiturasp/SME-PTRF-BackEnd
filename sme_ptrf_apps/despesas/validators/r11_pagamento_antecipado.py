from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class PagamentoAntecipadoValidator(AbstractDespesaValidator):
    """REG-011 — Pagamento antecipado (data_transacao < data_documento) exige motivos informados.
    REG-011 — Quando não há antecipação (dt >= dd), os motivos são descartados (fase apply).

    Legado: despesa_service.py:196-215 (_processar_pagamento_antecipado)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — pagamento antecipado exige motivos preenchidos.

        Levanta DespesaValidationError com detail={"detail": "mensagem"} quando
        data_transacao < data_documento e motivos ausentes.
        Ignorado quando data_transacao ou data_documento estão ausentes.
        """
        # despesa_service.py:200-201
        dt = ctx.data_transacao
        dd = ctx.data_documento

        if not (dt and dd):
            return ctx

        # despesa_service.py:203-210
        if dt < dd and not ctx.motivos_pagamento_antecipado and not ctx.outros_motivos:
            raise DespesaValidationError({
                "detail": (
                    "Quando a Data da transação for menor que a Data do Documento "
                    "é necessário informar os motivos do pagamento antecipado."
                ),
                "validator": self.__class__.__name__
            })

        return ctx

    def apply(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 2 — descarta motivos de pagamento antecipado quando não há antecipação (REG-011 apply).

        Zera ctx.motivos_pagamento_antecipado e ctx.outros_motivos quando data_transacao >= data_documento.

        Legado: despesa_service.py:211-213
        """
        dt = ctx.data_transacao
        dd = ctx.data_documento

        # despesa_service.py:211-213
        if dt and dd and dt >= dd:
            ctx.motivos_pagamento_antecipado = []
            ctx.outros_motivos = ""

        return ctx
