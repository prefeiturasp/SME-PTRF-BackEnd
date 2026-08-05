from datetime import date

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


class ContasImpostosValidator(AbstractDespesaValidator):
    """REG-008 — data_transacao do imposto >= data_inicio da conta do rateio de imposto.
    R11 — data_transacao do imposto <= data_encerramento da conta do rateio de imposto.

    Legado: validacao_despesa_service.py:209-239 (_validar_contas_impostos)
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        """Fase 1 — data_transacao de cada imposto deve estar dentro do intervalo da conta de seus rateios.

        Levanta DespesaValidationError com detail={"mensagem": "..."} no primeiro rateio inválido.
        Impostos sem data_transacao são ignorados.
        """
        for imposto in ctx.despesas_impostos:
            # validacao_despesa_service.py:212-214
            data_transacao = imposto.get("data_transacao")
            if not data_transacao:
                continue
            self._validar_rateios_do_imposto(imposto.get("rateios", []), data_transacao)
        return ctx

    @staticmethod
    def _validar_rateios_do_imposto(rateios: list, data_transacao: date) -> None:
        """Verifica datas de inicio/encerramento de conta para cada rateio de um imposto."""
        for rateio in rateios:
            # validacao_despesa_service.py:216-220
            conta = rateio.get("conta_associacao")
            if not conta:
                continue

            data_inicio = getattr(conta, "data_inicio", None)
            data_encerramento = getattr(conta, "data_encerramento", None)

            # validacao_despesa_service.py:222-228
            if data_inicio and data_inicio > data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios de imposto possuem conta com "
                        "data de início posterior à data de transação."
                    ),
                    "validator": "ContasImpostosValidator"
                })

            # validacao_despesa_service.py:230-239
            if data_encerramento and data_encerramento < data_transacao:
                raise DespesaValidationError({
                    "mensagem": (
                        "Um ou mais rateios de imposto possuem conta com "
                        "data de encerramento anterior à data de transação."
                    ),
                    "validator": "ContasImpostosValidator"
                })
