from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContasImpostosValidator(AbstractDespesaValidator):
    """R10 — data_transacao do imposto >= data_inicio da conta do rateio de imposto.
    R11 — data_transacao do imposto <= data_encerramento da conta do rateio de imposto.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        for imposto in ctx.despesas_impostos:
            data_transacao = imposto.get("data_transacao")
            if not data_transacao:
                continue

            for rateio in imposto.get("rateios", []):
                conta = rateio.get("conta_associacao")
                if not conta:
                    continue

                data_inicio = getattr(conta, "data_inicio", None)
                data_encerramento = getattr(conta, "data_encerramento", None)

                if data_inicio and data_inicio > data_transacao:
                    raise DespesaValidationError({
                        "mensagem": (
                            "Um ou mais rateios de imposto possuem conta com "
                            "data de início posterior à data de transação."
                        )
                    })

                if data_encerramento and data_encerramento < data_transacao:
                    raise DespesaValidationError({
                        "mensagem": (
                            "Um ou mais rateios de imposto possuem conta com "
                            "data de encerramento anterior à data de transação."
                        )
                    })

        return ctx
