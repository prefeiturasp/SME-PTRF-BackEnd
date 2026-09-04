from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_CONTA_ACAO_ASSOCIACAO = (
    "Conta e Ação do rateio devem pertencer à mesma associação da despesa."
)
MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO = (
    "Conta e Ação do imposto devem pertencer à mesma associação da despesa."
)


def _chave_associacao(obj):
    """Identidade comparável de uma Associação (pk, senão uuid)."""
    if obj is None:
        return None
    pk = getattr(obj, "pk", None)
    if pk is not None:
        return ("pk", pk)
    uuid = getattr(obj, "uuid", None)
    if uuid is not None:
        return ("uuid", str(uuid))
    return ("obj", obj)


def _associacao_de(obj):
    return getattr(obj, "associacao", None) if obj is not None else None


def _pertence_a_associacao(obj, associacao_despesa) -> bool:
    if obj is None or associacao_despesa is None:
        return True
    associacao_obj = _associacao_de(obj)
    if associacao_obj is None:
        return True
    return _chave_associacao(associacao_obj) == _chave_associacao(associacao_despesa)


class ContaAcaoMesmaAssociacaoValidator(AbstractDespesaValidator):
    """REG-071 — Conta e Ação de cada rateio (e dos impostos) são da associação da despesa.

    Impede payload com conta/ação de outra UE
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        associacao = ctx.associacao
        if associacao is None:
            return ctx

        self._validar_rateios(ctx.rateios, associacao, MSG_CONTA_ACAO_ASSOCIACAO)

        for imposto in ctx.despesas_impostos:
            imposto_associacao = imposto.get("associacao")
            if (
                imposto_associacao is not None and
                _chave_associacao(imposto_associacao) != _chave_associacao(associacao)
            ):
                raise DespesaValidationError({
                    "mensagem": MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO,
                    "validator": self.__class__.__name__,
                })
            self._validar_rateios(
                imposto.get("rateios") or [],
                associacao,
                MSG_IMPOSTO_CONTA_ACAO_ASSOCIACAO,
            )

        return ctx

    @staticmethod
    def _validar_rateios(rateios: list, associacao, mensagem: str) -> None:
        for rateio in rateios:
            conta = rateio.get("conta_associacao")
            acao = rateio.get("acao_associacao")
            if not _pertence_a_associacao(conta, associacao) or not _pertence_a_associacao(acao, associacao):
                raise DespesaValidationError({
                    "mensagem": mensagem,
                    "validator": "ContaAcaoMesmaAssociacaoValidator",
                })
