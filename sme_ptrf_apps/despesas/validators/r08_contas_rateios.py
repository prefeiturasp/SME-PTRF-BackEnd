from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContasRateiosValidator(AbstractDespesaValidator):
    """R08 — data_transacao >= data_inicio da conta de cada rateio.
    R09 — data_transacao <= data_encerramento da conta de cada rateio.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        data_transacao = ctx.data_transacao

        for rateio in ctx.rateios:
            conta = rateio.get("conta_associacao")
            if not conta:
                continue

            data_inicio = getattr(conta, "data_inicio", None)
            data_encerramento = getattr(conta, "data_encerramento", None)

            if data_transacao and data_inicio and data_inicio > data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de início "
                        "posterior à data de transação."
                    )
                })

            if data_transacao and data_encerramento and data_encerramento < data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de "
                        "encerramento anterior à data de transação."
                    )
                })

        return ctx
