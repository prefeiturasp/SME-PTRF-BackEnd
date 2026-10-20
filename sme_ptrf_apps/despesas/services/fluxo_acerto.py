"""Resolução do fluxo de acerto (create via documento / update via lançamento).

Usado pelo DespesasViewSet (serializer context → escolha do pipeline) quando a
flag 'despesas-pipeline' está ativa, e pelo DespesaService (marcar lançamento
atualizado / excluído), para não duplicar o critério de PC devolvida + acerto pendente.
"""
from __future__ import annotations

from typing import Optional

from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.core.models.analise_lancamento_prestacao_conta import (
    AnaliseLancamentoPrestacaoConta,
)
from sme_ptrf_apps.core.models.solicitacao_acerto_documento import SolicitacaoAcertoDocumento
from sme_ptrf_apps.core.models.solicitacao_acerto_lancamento import SolicitacaoAcertoLancamento
from sme_ptrf_apps.core.models.tipo_acerto_documento import TipoAcertoDocumento
from sme_ptrf_apps.core.models.tipo_acerto_lancamento import TipoAcertoLancamento


def extrair_uuid_solicitacao_acerto_do_request(request) -> Optional[str]:
    """Lê uuid_solicitacao_acerto de query string ou body."""
    if request is None:
        return None

    uuid_raw = None
    if hasattr(request, "query_params"):
        uuid_raw = request.query_params.get("uuid_solicitacao_acerto")
    if not uuid_raw and hasattr(request, "data"):
        try:
            uuid_raw = request.data.get("uuid_solicitacao_acerto")
        except Exception:
            uuid_raw = None

    if not uuid_raw:
        return None
    return str(uuid_raw)


def resolver_uuid_solicitacao_acerto_create(request) -> Optional[str]:
    """Fluxo 3 — create via inclusão de gasto.

    Exige SolicitacaoAcertoDocumento existente quando o uuid é informado.
    """
    uuid_raw = extrair_uuid_solicitacao_acerto_do_request(request)
    if not uuid_raw:
        return None

    if not SolicitacaoAcertoDocumento.objects.filter(uuid=uuid_raw).exists():
        raise ValidationError({
            "uuid_solicitacao_acerto": "Solicitação de acerto não encontrada.",
        })

    return uuid_raw


def obter_analise_lancamento_edicao_pendente(despesa):
    """Retorna AnaliseLancamentoPrestacaoConta pendente de edição, se houver.

    Critério alinhado ao legado de DespesaService._marcar_lancamento_como_atualizado:
    PC devolvida + análise de gasto pendente + solicitação EDICAO_LANCAMENTO pendente.
    """
    if despesa is None:
        return None

    prestacao_conta = despesa.prestacao_conta
    if not prestacao_conta or prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA:
        return None

    lancamento_analise = (
        AnaliseLancamentoPrestacaoConta.objects.filter(
            despesa=despesa,
            lancamento_atualizado=False,
            tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
            status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
        )
        .first()
    )

    if not lancamento_analise:
        return None

    possui_solicitacao_pendente = (
        lancamento_analise.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
            status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
        )
        .exists()
    )

    if not possui_solicitacao_pendente:
        return None

    return lancamento_analise


def obter_analise_lancamento_exclusao_pendente(despesa):
    """Retorna AnaliseLancamentoPrestacaoConta pendente de exclusão, se houver.

    Critério espelhado da edição (REG-031), para categoria EXCLUSAO_LANCAMENTO:
    PC devolvida + análise de gasto pendente + solicitação EXCLUSAO pendente.
    """
    if despesa is None:
        return None

    prestacao_conta = despesa.prestacao_conta
    if not prestacao_conta or prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA:
        return None

    lancamento_analise = (
        AnaliseLancamentoPrestacaoConta.objects.filter(
            despesa=despesa,
            lancamento_excluido=False,
            tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
            status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
        )
        .first()
    )

    if not lancamento_analise:
        return None

    possui_solicitacao_pendente = (
        lancamento_analise.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
            status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
        )
        .exists()
    )

    if not possui_solicitacao_pendente:
        return None

    return lancamento_analise


def obter_analise_lancamento_edicao_em_devolucao(despesa):
    """Análise de edição de gasto enquanto a PC da despesa está DEVOLVIDA.

    Diferente de ``obter_analise_lancamento_edicao_pendente``: permite re-editar
    mesmo após marcar realização / ``lancamento_atualizado=True`` — enquanto a
    devolução estiver aberta (REG-019 não se aplica; vale REG-007).
    """
    if despesa is None:
        return None

    prestacao_conta = despesa.prestacao_conta
    if not prestacao_conta or prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA:
        return None

    return (
        AnaliseLancamentoPrestacaoConta.objects.filter(
            despesa=despesa,
            tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
            solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=(
                TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
            ),
        )
        .distinct()
        .first()
    )


def obter_solicitacao_inclusao_gasto_da_despesa(despesa, uuid_solicitacao_acerto=None):
    """INCLUSAO_GASTO vinculada à despesa em PC DEVOLVIDA (pendente ou já realizada)."""
    if despesa is None:
        return None

    qs = (
        SolicitacaoAcertoDocumento.objects.filter(
            despesa_incluida=despesa,
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
        )
        .select_related(
            "analise_documento__analise_prestacao_conta__prestacao_conta",
            "tipo_acerto",
        )
    )
    if uuid_solicitacao_acerto:
        qs = qs.filter(uuid=uuid_solicitacao_acerto)

    for solicitacao in qs:
        try:
            prestacao = (
                solicitacao.analise_documento
                .analise_prestacao_conta
                .prestacao_conta
            )
        except AttributeError:
            continue
        if prestacao and prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
            return solicitacao
    return None


def resolver_uuid_solicitacao_acerto_update(despesa, request=None) -> Optional[str]:
    """Fluxo 4 — update via acerto.

    Preferência: uuid explícito no request; senão infere edição de lançamento
    ou inclusão de gasto vinculada, enquanto a PC estiver DEVOLVIDA.
    """
    uuid_explicito = extrair_uuid_solicitacao_acerto_do_request(request)
    if uuid_explicito:
        return uuid_explicito

    lancamento_analise = obter_analise_lancamento_edicao_em_devolucao(despesa)
    if lancamento_analise:
        solicitacao = (
            lancamento_analise.solicitacoes_de_ajuste_da_analise.filter(
                tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
            )
            .order_by("-id")
            .first()
        )
        if solicitacao:
            return str(solicitacao.uuid)

    solicitacao_doc = obter_solicitacao_inclusao_gasto_da_despesa(despesa)
    if solicitacao_doc:
        return str(solicitacao_doc.uuid)

    return None


def obter_solicitacao_inclusao_gasto_pendente(uuid_solicitacao_acerto):
    """Create via acerto: SolicitacaoAcertoDocumento INCLUSAO_GASTO pendente em PC DEVOLVIDA."""
    if not uuid_solicitacao_acerto:
        return None

    solicitacao = (
        SolicitacaoAcertoDocumento.objects.filter(
            uuid=uuid_solicitacao_acerto,
            status_realizacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_PENDENTE,
            tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
        )
        .select_related(
            "analise_documento__analise_prestacao_conta__prestacao_conta",
            "tipo_acerto",
        )
        .first()
    )
    if not solicitacao:
        return None

    try:
        prestacao = (
            solicitacao.analise_documento
            .analise_prestacao_conta
            .prestacao_conta
        )
    except AttributeError:
        return None

    if not prestacao or prestacao.status != PrestacaoConta.STATUS_DEVOLVIDA:
        return None

    return solicitacao


def contexto_acerto_create_valido(uuid_solicitacao_acerto) -> bool:
    return obter_solicitacao_inclusao_gasto_pendente(uuid_solicitacao_acerto) is not None


def contexto_acerto_update_valido(despesa, uuid_solicitacao_acerto=None) -> bool:
    """Update via acerto enquanto a PC estiver DEVOLVIDA.

    Aceita re-edição após marcar realização (edição de lançamento ou inclusão
    de gasto já vinculada). Uuid explícito, se houver, precisa bater com o vínculo.
    """
    sol_doc = obter_solicitacao_inclusao_gasto_da_despesa(despesa, uuid_solicitacao_acerto)
    if sol_doc:
        return True

    # Uuid de documento que não pertence a esta despesa → inválido
    if uuid_solicitacao_acerto and SolicitacaoAcertoDocumento.objects.filter(
        uuid=uuid_solicitacao_acerto,
        tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
    ).exists():
        return False

    lancamento_analise = obter_analise_lancamento_edicao_em_devolucao(despesa)
    if not lancamento_analise:
        return False

    if not uuid_solicitacao_acerto:
        return True

    return (
        lancamento_analise.solicitacoes_de_ajuste_da_analise.filter(
            uuid=uuid_solicitacao_acerto,
            tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
        )
        .exists()
    )
