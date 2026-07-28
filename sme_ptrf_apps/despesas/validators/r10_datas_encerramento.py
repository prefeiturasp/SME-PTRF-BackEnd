from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class DatasEncerramentoValidator(AbstractDespesaValidator):
    """REG-010 — Data de documento/transação não pode ser posterior ao encerramento da associação.

    Legado: despesa_service.py:165-182 (_validar_datas)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — data_documento e data_transacao não podem ultrapassar data_de_encerramento da associação.

        Levanta DespesaValidationError com detail={"erro_data_de_encerramento": True, ...} quando violado.
        Ignorado quando a associação não possui data_de_encerramento.
        """
        # despesa_service.py:167-168
        associacao = ctx.associacao
        data_encerramento = associacao.data_de_encerramento if associacao else None

        # despesa_service.py:170-182
        if data_encerramento:
            for data in (ctx.data_documento, ctx.data_transacao):
                if data and data > data_encerramento:
                    dt_encerramento_formatada = data_encerramento.strftime("%d/%m/%Y")
                    raise DespesaValidationError({
                        "erro_data_de_encerramento": True,
                        "data_de_encerramento": dt_encerramento_formatada,
                        "mensagem": (
                            "A data de documento e/ou data do pagamento não pode ser posterior "
                            f"à {dt_encerramento_formatada}, data de encerramento da associação."
                        ),
                        "validator": self.__class__.__name__
                    })

        return ctx
