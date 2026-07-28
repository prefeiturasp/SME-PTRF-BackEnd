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

        validacao_periodo_fechado = False

        for periodo in bem_produzido_context.periodos:
            if not periodo or not bem_produzido_context.associacao:
                validacao_periodo_fechado = True
                break

            if periodo.encerrado:
                validacao_periodo_fechado = True
                break

            prestacao_conta = PrestacaoConta.by_periodo(
                associacao=bem_produzido_context.associacao,
                periodo=periodo
            )

            if prestacao_conta and prestacao_conta.status in status_pc_entregue:
                validacao_periodo_fechado = True
                break

        if validacao_periodo_fechado:
            raise SituacaoPatrimonialValidationError(
                title="Período fechado",
                detail="O período está bloqueado para realização de alterações."
            )

        return bem_produzido_context
