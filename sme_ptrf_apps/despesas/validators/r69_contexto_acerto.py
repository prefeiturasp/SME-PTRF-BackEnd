"""REG-069 — Contexto de acerto válido (PC devolvida + solicitação compatível).

Só entra nos pipelines 3 e 4. Create exige inclusão de gasto pendente; update
aceita re-edição enquanto a PC estiver DEVOLVIDA (mesmo após marcar realizado).
"""
from sme_ptrf_apps.despesas.services.fluxo_acerto import (
    contexto_acerto_create_valido,
    contexto_acerto_update_valido,
)

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_CONTEXTO_ACERTO_INVALIDO = (
    "Não é permitido salvar esta despesa fora de uma solicitação de acerto "
    "pendente em prestação de contas devolvida."
)


class ContextoAcertoValidator(AbstractDespesaValidator):
    """REG-069 — Fluxos 3 e 4: exige PC devolvida + solicitação compatível."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.is_acerto:
            return ctx

        if ctx.is_create:
            contexto_valido = contexto_acerto_create_valido(ctx.uuid_solicitacao_acerto)
        else:
            contexto_valido = contexto_acerto_update_valido(
                ctx.despesa_instance,
                ctx.uuid_solicitacao_acerto,
            )

        if contexto_valido:
            return ctx

        raise DespesaValidationError({
            "non_field_errors": MSG_CONTEXTO_ACERTO_INVALIDO,
            "mensagem": MSG_CONTEXTO_ACERTO_INVALIDO,
            "uuid_solicitacao_acerto": MSG_CONTEXTO_ACERTO_INVALIDO,
            "validator": self.__class__.__name__,
        })
