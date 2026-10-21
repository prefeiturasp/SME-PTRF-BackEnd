from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
from sme_ptrf_apps.situacao_patrimonial.services.bem_produzido_service import BemProduzidoService

from .base import AbstractBemProduzidoValidator, SituacaoPatrimonialValidationError
from .context import BemProduzidoDtoContext


class BloqueioEdicaoBemProduzidoCompletoPeriodoFechadoValidator(AbstractBemProduzidoValidator):
    """Bloqueia a edição de um bem completo quando a PC da despesa mais recente está fechada."""

    def validate(self, bem_produzido_context: BemProduzidoDtoContext) -> BemProduzidoDtoContext:
        if bem_produzido_context.status != BemProduzido.STATUS_COMPLETO:
            return bem_produzido_context

        if bem_produzido_context.bem_produzido is None:
            return bem_produzido_context

        if BemProduzidoService.bem_produzido_em_modo_visualizacao(bem_produzido_context.bem_produzido):
            raise SituacaoPatrimonialValidationError({
                "titulo": "Período fechado",
                "mensagem": "O período está bloqueado para realização de alterações.",
                "validator": self.__class__.__name__
            })

        return bem_produzido_context
