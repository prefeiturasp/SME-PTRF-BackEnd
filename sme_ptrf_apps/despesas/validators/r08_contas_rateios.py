from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContasRateiosValidator(AbstractDespesaValidator):
    """R08 — data_transacao >= data_inicio da conta de cada rateio.
    R09 — data_transacao <= data_encerramento da conta de cada rateio.

    Legado: validacao_despesa_service.py:185-207 (_validar_contas_rateios)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — data_transacao deve estar dentro do intervalo [data_inicio, data_encerramento] da conta.

        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro rateio inválido.
        Rateios sem conta_associacao são ignorados.
        """
        # validacao_despesa_service.py:186
        data_transacao = ctx.data_transacao

        for rateio in ctx.rateios:
            # validacao_despesa_service.py:187-191
            conta = rateio.get("conta_associacao")
            if not conta:
                continue

            data_inicio = getattr(conta, "data_inicio", None)
            data_encerramento = getattr(conta, "data_encerramento", None)

            # validacao_despesa_service.py:193-199
            if data_transacao and data_inicio and data_inicio > data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de início "
                        "posterior à data de transação."
                    ),
                    "validator": self.__class__.__name__
                })

            # validacao_despesa_service.py:201-207
            if data_transacao and data_encerramento and data_encerramento < data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de "
                        "encerramento anterior à data de transação."
                    ),
                    "validator": self.__class__.__name__
                })

        return ctx
