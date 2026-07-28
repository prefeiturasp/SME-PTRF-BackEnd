from .base import AbstractBemProduzidoValidator, SituacaoPatrimonialValidationError
from sme_ptrf_apps.core.models import PrestacaoConta
from .context import BemProduzidoDtoContext


class PeriodoFechadoValidator(AbstractBemProduzidoValidator):
    """Valida se o recurso do bem produzido é obrigatório para o fluxo atual."""

    def validate(self, bem_produzido_context: BemProduzidoDtoContext) -> BemProduzidoDtoContext:

        status_pc_entregue = [
            status for status in PrestacaoConta.STATUS_NOMES.keys()
            if status != PrestacaoConta.STATUS_NAO_APRESENTADA
        ]

        for periodo in bem_produzido_context.periodos:
            if not bem_produzido_context.associacao:
                raise SituacaoPatrimonialValidationError({
                    "titulo": "Bem produzido sem associação",
                    "mensagem": "O período está bloqueado para realização de alterações.",
                    "validator": self.__class__.__name__
                })

            prestacao_conta = PrestacaoConta.by_periodo(
                associacao=bem_produzido_context.associacao,
                periodo=periodo
            )

            prestacao_conta_entregue = prestacao_conta and prestacao_conta.status in status_pc_entregue

            if prestacao_conta_entregue or periodo.encerrado:
                raise SituacaoPatrimonialValidationError({
                    "titulo": "Período fechado",
                    "mensagem": "O período está bloqueado para realização de alterações.",
                    "validator": self.__class__.__name__
                })

        return bem_produzido_context
