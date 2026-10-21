"""Testes da resolução de fluxo acerto (create / update)."""
import datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from rest_framework.exceptions import ValidationError
from waffle.testutils import override_flag

from sme_ptrf_apps.core.models import (
    AnaliseLancamentoPrestacaoConta,
    PrestacaoConta,
    SolicitacaoAcertoLancamento,
    TipoAcertoLancamento,
)
from sme_ptrf_apps.despesas.services.fluxo_acerto import (
    extrair_uuid_solicitacao_acerto_do_request,
    obter_analise_lancamento_edicao_pendente,
    obter_analise_lancamento_exclusao_pendente,
    resolver_uuid_solicitacao_acerto_create,
    resolver_uuid_solicitacao_acerto_update,
)


pytestmark = pytest.mark.django_db


def _request_com_uuid(uuid_value=None, via="data"):
    data = {}
    query = {}
    if uuid_value is not None:
        if via == "data":
            data["uuid_solicitacao_acerto"] = uuid_value
        else:
            query["uuid_solicitacao_acerto"] = uuid_value
    return SimpleNamespace(
        data=data,
        query_params=query,
    )


def criar_cenario_edicao_pendente(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    lancamento_atualizado=False,
):
    prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )

    analise_prestacao = analise_prestacao_conta_factory()
    tipo_acerto = tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO
    )
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento="123456",
        cpf_cnpj_fornecedor="11.478.276/0001-04",
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        nome_fornecedor="Fornecedor SA",
        valor_total=50.00,
        valor_recursos_proprios=0,
    )
    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
        despesa=despesa,
        lancamento_atualizado=lancamento_atualizado,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
    )
    solicitacao = solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    )
    return despesa, analise_lancamento, solicitacao


def criar_cenario_exclusao_pendente(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
    status_prestacao=PrestacaoConta.STATUS_DEVOLVIDA,
    lancamento_excluido=False,
):
    prestacao_conta_factory(
        status=status_prestacao,
        periodo=periodo_2020_2,
        associacao=associacao,
    )

    analise_prestacao = analise_prestacao_conta_factory()
    tipo_acerto = tipo_acerto_lancamento_factory(
        categoria=TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO
    )
    despesa = despesa_factory(
        associacao=associacao,
        numero_documento="654321",
        cpf_cnpj_fornecedor="11.478.276/0001-04",
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        nome_fornecedor="Fornecedor SA",
        valor_total=50.00,
        valor_recursos_proprios=0,
    )
    analise_lancamento = analise_lancamento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
        despesa=despesa,
        lancamento_excluido=lancamento_excluido,
        tipo_lancamento=AnaliseLancamentoPrestacaoConta.TIPO_LANCAMENTO_GASTO,
        status_realizacao=AnaliseLancamentoPrestacaoConta.STATUS_REALIZACAO_PENDENTE,
    )
    solicitacao = solicitacao_acerto_lancamento_factory(
        analise_lancamento=analise_lancamento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoLancamento.STATUS_REALIZACAO_PENDENTE,
    )
    return despesa, analise_lancamento, solicitacao


def test_extrair_uuid_do_body():
    request = _request_com_uuid("abc-123", via="data")
    assert extrair_uuid_solicitacao_acerto_do_request(request) == "abc-123"


def test_extrair_uuid_da_query():
    request = _request_com_uuid("abc-456", via="query")
    assert extrair_uuid_solicitacao_acerto_do_request(request) == "abc-456"


def test_extrair_uuid_ausente():
    assert extrair_uuid_solicitacao_acerto_do_request(_request_com_uuid()) is None
    assert extrair_uuid_solicitacao_acerto_do_request(None) is None


def test_resolver_create_sem_uuid():
    assert resolver_uuid_solicitacao_acerto_create(_request_com_uuid()) is None


def test_resolver_create_uuid_valido(solicitacao_acerto_documento_factory):
    solicitacao = solicitacao_acerto_documento_factory()
    request = _request_com_uuid(str(solicitacao.uuid))
    assert resolver_uuid_solicitacao_acerto_create(request) == str(solicitacao.uuid)


def test_resolver_create_uuid_invalido():
    request = _request_com_uuid(str(uuid4()))
    with pytest.raises(ValidationError) as exc:
        resolver_uuid_solicitacao_acerto_create(request)
    assert "uuid_solicitacao_acerto" in exc.value.detail


def test_resolver_update_infere_solicitacao_pendente(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _, solicitacao = criar_cenario_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )

    uuid_resolvido = resolver_uuid_solicitacao_acerto_update(despesa)
    assert uuid_resolvido == str(solicitacao.uuid)
    assert obter_analise_lancamento_edicao_pendente(despesa) is not None


def test_resolver_update_sem_pc_devolvida(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _, _ = criar_cenario_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_EM_ANALISE,
    )

    assert resolver_uuid_solicitacao_acerto_update(despesa) is None
    assert obter_analise_lancamento_edicao_pendente(despesa) is None


def test_resolver_update_infere_mesmo_apos_lancamento_atualizado(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    """Re-edição durante devolução: ainda resolve fluxo 4 após marcar atualizado."""
    despesa, _, solicitacao = criar_cenario_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        lancamento_atualizado=True,
    )

    assert obter_analise_lancamento_edicao_pendente(despesa) is None
    assert resolver_uuid_solicitacao_acerto_update(despesa) == str(solicitacao.uuid)


def test_resolver_update_infere_inclusao_gasto_vinculada(
    prestacao_conta_factory,
    analise_prestacao_conta_factory,
    analise_documento_prestacao_conta_factory,
    tipo_acerto_documento_factory,
    solicitacao_acerto_documento_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    from sme_ptrf_apps.core.models import SolicitacaoAcertoDocumento, TipoAcertoDocumento

    prestacao = prestacao_conta_factory(
        status=PrestacaoConta.STATUS_DEVOLVIDA,
        periodo=periodo_2020_2,
        associacao=associacao,
    )
    analise_prestacao = analise_prestacao_conta_factory(prestacao_conta=prestacao)
    analise_documento = analise_documento_prestacao_conta_factory(
        analise_prestacao_conta=analise_prestacao,
    )
    tipo_acerto = tipo_acerto_documento_factory(
        categoria=TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
    )
    despesa = despesa_factory(
        associacao=associacao,
        data_transacao=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        data_documento=periodo_2020_2.data_inicio_realizacao_despesas + datetime.timedelta(days=3),
        valor_total=50.00,
    )
    solicitacao = solicitacao_acerto_documento_factory(
        analise_documento=analise_documento,
        tipo_acerto=tipo_acerto,
        status_realizacao=SolicitacaoAcertoDocumento.STATUS_REALIZACAO_REALIZADO,
        despesa_incluida=despesa,
    )

    assert resolver_uuid_solicitacao_acerto_update(despesa) == str(solicitacao.uuid)


def test_resolver_update_prefere_uuid_explicito_do_request(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _, _ = criar_cenario_edicao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )
    uuid_explicito = str(uuid4())
    request = _request_com_uuid(uuid_explicito)

    assert resolver_uuid_solicitacao_acerto_update(despesa, request) == uuid_explicito


def test_viewset_context_nao_injeta_uuid_sem_flag(
    solicitacao_acerto_documento_factory,
    recurso_factory,
):
    """Sem despesas-pipeline, uuid no body não entra no context (legado intacto)."""
    from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet

    solicitacao = solicitacao_acerto_documento_factory()
    request = SimpleNamespace(
        data={"uuid_solicitacao_acerto": str(solicitacao.uuid)},
        query_params={},
        recurso=recurso_factory(),
    )

    view = DespesasViewSet()
    view.action = "create"
    view.request = request
    view.format_kwarg = None

    context = view.get_serializer_context()
    assert "uuid_solicitacao_acerto" not in context


@override_flag('despesas-pipeline', active=True)
def test_viewset_context_injeta_uuid_com_flag(
    solicitacao_acerto_documento_factory,
    recurso_factory,
):
    """Com despesas-pipeline, uuid válido no body entra no context (fluxo 3)."""
    from sme_ptrf_apps.despesas.api.views.despesas_viewset import DespesasViewSet

    solicitacao = solicitacao_acerto_documento_factory()
    request = SimpleNamespace(
        data={"uuid_solicitacao_acerto": str(solicitacao.uuid)},
        query_params={},
        recurso=recurso_factory(),
    )

    view = DespesasViewSet()
    view.action = "create"
    view.request = request
    view.format_kwarg = None

    context = view.get_serializer_context()
    assert context.get("uuid_solicitacao_acerto") == str(solicitacao.uuid)


def test_obter_analise_exclusao_pendente_ok(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, analise_lancamento, _ = criar_cenario_exclusao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
    )

    resultado = obter_analise_lancamento_exclusao_pendente(despesa)
    assert resultado is not None
    assert resultado.uuid == analise_lancamento.uuid


def test_obter_analise_exclusao_pendente_sem_pc_devolvida(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _, _ = criar_cenario_exclusao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        status_prestacao=PrestacaoConta.STATUS_EM_ANALISE,
    )

    assert obter_analise_lancamento_exclusao_pendente(despesa) is None


def test_obter_analise_exclusao_pendente_ja_excluido(
    prestacao_conta_factory,
    solicitacao_acerto_lancamento_factory,
    analise_prestacao_conta_factory,
    tipo_acerto_lancamento_factory,
    analise_lancamento_prestacao_conta_factory,
    despesa_factory,
    associacao,
    periodo_2020_2,
):
    despesa, _, _ = criar_cenario_exclusao_pendente(
        prestacao_conta_factory,
        solicitacao_acerto_lancamento_factory,
        analise_prestacao_conta_factory,
        tipo_acerto_lancamento_factory,
        analise_lancamento_prestacao_conta_factory,
        despesa_factory,
        associacao,
        periodo_2020_2,
        lancamento_excluido=True,
    )

    assert obter_analise_lancamento_exclusao_pendente(despesa) is None
