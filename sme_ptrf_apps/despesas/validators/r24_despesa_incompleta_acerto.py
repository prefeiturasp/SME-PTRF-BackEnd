"""REG-024 — Em fluxo de acerto, despesa incompleta não pode ser salva.

Espelha Despesa.cadastro_completo / RateioDespesa.cadastro_completo,
mas sempre valida rateios (no model, create com id=None pula rateios).
"""
from decimal import Decimal

from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

from .base import AbstractDespesaValidator, DespesaValidationError
from .context import DespesaDtoContext


MSG_INCOMPLETA_ACERTO = (
    "Não é possível cadastrar uma despesa incompleta através de uma "
    "solicitação de inclusão ou ajuste da DRE."
)


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _rateio_completo(rateio, eh_sem_comprovacao_fiscal: bool) -> bool:
    conta = _get(rateio, "conta_associacao")
    acao = _get(rateio, "acao_associacao")
    aplicacao = _get(rateio, "aplicacao_recurso")
    valor_rateio = _get(rateio, "valor_rateio") or 0
    saida_externo = bool(_get(rateio, "saida_de_recurso_externo") or False)
    eh_sem_comp_rateio = bool(
        _get(rateio, "eh_despesa_sem_comprovacao_fiscal") or eh_sem_comprovacao_fiscal
    )

    completo = bool(conta and acao and aplicacao and Decimal(str(valor_rateio)) > 0)

    if completo and not saida_externo and not eh_sem_comp_rateio:
        completo = completo and bool(_get(rateio, "especificacao_material_servico"))

    if completo and aplicacao == APLICACAO_CUSTEIO:
        if not saida_externo and not eh_sem_comp_rateio:
            completo = completo and bool(_get(rateio, "tipo_custeio"))
    elif completo and aplicacao == APLICACAO_CAPITAL:
        qtd = _get(rateio, "quantidade_itens_capital") or 0
        valor_item = _get(rateio, "valor_item_capital") or 0
        completo = completo and int(qtd) > 0 and Decimal(str(valor_item)) > 0
        nao_exibir = bool(_get(rateio, "nao_exibir_em_rel_bens") or False)
        if not (eh_sem_comp_rateio or nao_exibir):
            completo = completo and bool(_get(rateio, "numero_processo_incorporacao_capital"))

    return bool(completo)


def _despesa_completa(ctx: DespesaDtoContext) -> bool:
    completo = bool(ctx.data_transacao) and ctx.valor_total > 0
    eh_imposto = False  # despesa principal do acerto não é imposto gerado

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal and not eh_imposto:
        completo = completo and bool(ctx.cpf_cnpj_fornecedor)

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal and not eh_imposto:
        completo = completo and bool(ctx.nome_fornecedor)

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal:
        completo = completo and bool(ctx.tipo_transacao)

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal:
        completo = completo and bool(ctx.tipo_documento)

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal and not eh_imposto:
        completo = completo and bool(ctx.data_documento)

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal and ctx.tipo_documento:
        if getattr(ctx.tipo_documento, "numero_documento_digitado", False):
            completo = completo and ctx.numero_documento != ""

    if completo and not ctx.eh_despesa_sem_comprovacao_fiscal and ctx.tipo_transacao:
        if getattr(ctx.tipo_transacao, "tem_documento", False):
            completo = completo and ctx.documento_transacao != ""

    if completo and not ctx.eh_despesa_reconhecida_pela_associacao:
        completo = completo and bool((ctx.numero_boletim_de_ocorrencia or "").strip())

    if completo:
        for rateio in ctx.rateios:
            if not _rateio_completo(rateio, ctx.eh_despesa_sem_comprovacao_fiscal):
                return False

    return bool(completo)


class DespesaIncompletaAcertoValidator(AbstractDespesaValidator):
    """REG-024 — Fluxos 3 e 4: despesa incompleta é bloqueada."""

    def validate(self, ctx: DespesaDtoContext) -> DespesaDtoContext:
        if _despesa_completa(ctx):
            return ctx

        raise DespesaValidationError({
            "non_field_errors": MSG_INCOMPLETA_ACERTO,
            "mensagem": MSG_INCOMPLETA_ACERTO,
            "validator": self.__class__.__name__,
        })
