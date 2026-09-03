from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_ASSOCIACAO_IMUTAVEL = (
    "Não é permitido alterar a associação da despesa."
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


class AssociacaoImutavelValidator(AbstractDespesaValidator):
    """REG-070 — Associação da despesa não muda na edição.

    O front, ao abrir `/edicao-de-despesa/:uuid`, troca `associacao` (e a dos
    rateios) pelo UUID da UE no localStorage. Sem esta regra, um PUT na sessão
    de outra escola reassocia o lançamento.
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        instance = ctx.despesa_instance
        if instance is None:
            return ctx

        associacao_gravada = getattr(instance, "associacao", None)
        if associacao_gravada is None or ctx.associacao is None:
            return ctx

        if _chave_associacao(associacao_gravada) != _chave_associacao(ctx.associacao):
            raise DespesaValidationError({
                "mensagem": MSG_ASSOCIACAO_IMUTAVEL,
                "validator": self.__class__.__name__,
            })

        return ctx
