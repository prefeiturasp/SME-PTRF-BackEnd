from .base import AbstractBemProduzidoValidator, SituacaoPatrimonialValidationError
from sme_ptrf_apps.core.models import PrestacaoConta
from .context import BemProduzidoDtoContext


class PeriodoFechadoValidator(AbstractBemProduzidoValidator):
    """Valida se todos os períodos do bem produzido estão bloqueados."""

    def validate(self, bem_produzido_context: BemProduzidoDtoContext) -> BemProduzidoDtoContext:

        if not bem_produzido_context.associacao:
            raise SituacaoPatrimonialValidationError({
                "titulo": "Bem produzido sem associação",
                "mensagem": "O bem produzido deve possuir uma associação.",
                "validator": self.__class__.__name__
            })

        todos_periodos_bloqueados = True

        for periodo in bem_produzido_context.periodos:
            prestacao_conta = PrestacaoConta.by_periodo(
                associacao=bem_produzido_context.associacao,
                periodo=periodo
            )

            periodo_bloqueado = (
                periodo.encerrado and
                prestacao_conta is not None and
                prestacao_conta.status != PrestacaoConta.STATUS_NAO_APRESENTADA
            )

            # Se existir ao menos um período desbloqueado,
            # já pode permitir a exclusão.
            if not periodo_bloqueado:
                todos_periodos_bloqueados = False
                break

        if todos_periodos_bloqueados:
            raise SituacaoPatrimonialValidationError({
                "titulo": "Período fechado",
                "mensagem": "O período está bloqueado para realização de alterações.",
                "validator": self.__class__.__name__
            })

        return bem_produzido_context
