"""REG-007 — Data dentro do período da PC devolvida para acertos.

No update: usa ``despesa.prestacao_conta``.
No create via acerto (Fluxo 3): resolve a PC pela solicitação de acerto.
"""
from sme_ptrf_apps.core.models import Periodo
from sme_ptrf_apps.core.models.solicitacao_acerto_documento import SolicitacaoAcertoDocumento
from sme_ptrf_apps.core.models.solicitacao_acerto_lancamento import SolicitacaoAcertoLancamento

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_PERIODO_DEVOLUCAO = "Permitido apenas datas dentro do período referente à devolução."


def _pc_da_solicitacao_acerto(uuid_solicitacao_acerto):
    """Prestação de Contas vinculada à solicitação (documento ou lançamento)."""
    if not uuid_solicitacao_acerto:
        return None

    solicitacao_doc = (
        SolicitacaoAcertoDocumento.objects.filter(uuid=uuid_solicitacao_acerto)
        .select_related(
            "analise_documento__analise_prestacao_conta__prestacao_conta__periodo",
        )
        .first()
    )
    if solicitacao_doc:
        try:
            return (
                solicitacao_doc.analise_documento
                .analise_prestacao_conta
                .prestacao_conta
            )
        except AttributeError:
            return None

    solicitacao_lanc = (
        SolicitacaoAcertoLancamento.objects.filter(uuid=uuid_solicitacao_acerto)
        .select_related(
            "analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo",
        )
        .first()
    )
    if solicitacao_lanc:
        try:
            return (
                solicitacao_lanc.analise_lancamento
                .analise_prestacao_conta
                .prestacao_conta
            )
        except AttributeError:
            return None

    return None


def _obter_pc_para_validacao(ctx: DespesaDtoContext):
    instance = ctx.despesa_instance
    if instance is not None:
        pc = getattr(instance, "prestacao_conta", None)
        if pc:
            return pc

    # Create via acerto: ainda não há despesa; usa a PC da solicitação.
    if ctx.is_acerto:
        return _pc_da_solicitacao_acerto(ctx.uuid_solicitacao_acerto)

    return None


class PeriodoPcDevolvidaValidator(AbstractDespesaValidator):
    """REG-007 — Data da despesa deve estar no período da PC devolvida.

    Também resolve e injeta ctx.periodo para validators posteriores.

    Legado: validacao_despesa_service.py:154-167 (só update).
    Pipeline: também no create via acerto (paridade com o front).
    """

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if not ctx.data_transacao:
            return ctx

        recurso = ctx.recurso_efetivo
        if not recurso:
            return ctx

        periodo = Periodo.da_data_por_recurso(ctx.data_transacao, recurso)
        ctx.periodo = periodo

        pc = _obter_pc_para_validacao(ctx)
        if not pc:
            return ctx

        if (
            pc.devolvida_para_acertos and
            periodo and
            periodo.referencia != pc.periodo.referencia
        ):
            raise DespesaValidationError({
                "mensagem": MSG_PERIODO_DEVOLUCAO,
                "data_transacao": MSG_PERIODO_DEVOLUCAO,
                "validator": self.__class__.__name__,
            })

        return ctx
