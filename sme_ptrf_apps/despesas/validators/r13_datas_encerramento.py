from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class DatasEncerramentoValidator(AbstractDespesaValidator):
    """R13 — Data de documento/transação não pode ser posterior ao encerramento da associação."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        associacao = ctx.associacao
        data_encerramento = getattr(associacao, "data_de_encerramento", None) if associacao else None

        if not data_encerramento:
            return ctx

        for data in (ctx.data_documento, ctx.data_transacao):
            if data and data > data_encerramento:
                dt_formatada = data_encerramento.strftime("%d/%m/%Y")
                raise DespesaValidationError({
                    "erro_data_de_encerramento": True,
                    "data_de_encerramento": dt_formatada,
                    "mensagem": (
                        "A data de documento e/ou data do pagamento não pode ser posterior "
                        f"à {dt_formatada}, data de encerramento da associação."
                    ),
                })

        return ctx
