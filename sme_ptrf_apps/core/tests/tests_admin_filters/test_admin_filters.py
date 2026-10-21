from unittest.mock import MagicMock

from django.test import RequestFactory

from sme_ptrf_apps.core.admin import DreArquivoDownloadFilter, DreListFilter
from sme_ptrf_apps.core.admin_filters.recurso_filters import (
    AcaoAssociacaoAListFilter,
    AnalisePrestacaoContaFilter,
    AnaliseConsolidadoDreListFilter,
    AtaListFilter,
    DemonstrativoFinanceiroListFilter,
    DevolucaoPrestacaoContaFilter,
    ObservacaoConciliacaoFilter,
    PeriodoRecursoListFilter,
    PrestacaoContaListFilter,
    RecursoAssociacaoListFilter,
    RecursoContasAssociacaoListFilter,
    RecursoListFilter,
    RelacaoBensListFilter,
)
from sme_ptrf_apps.core.models import ArquivoDownload

from .conftest import make_filter

RECURSO_ID = "999"


def test_recurso_list_filter_lookups(recursos, request_factory_admin, recurso_list_filter):
    ptrf, premium = recursos

    filtro = recurso_list_filter

    resultado = list(filtro.lookups(request_factory_admin, None))

    esperado = [
        (str(premium.id), "premium"),
        (str(ptrf.id), "ptrf"),
    ]

    for item in esperado:
        assert item in resultado


def test_recurso_list_filter_lookups_excludes_inactive(recursos, request_factory_admin, recurso_list_filter):
    resultado = list(recurso_list_filter.lookups(request_factory_admin, None))
    nomes = [nome for _, nome in resultado]
    assert "inativo" not in nomes


def _mock_qs():
    qs = MagicMock()
    qs.filter.return_value.distinct.return_value = MagicMock()
    return qs


def _assert_no_filter(filter_instance):
    qs = _mock_qs()
    result = filter_instance.queryset(None, qs)
    assert result is qs
    qs.filter.assert_not_called()


def _assert_filtered(filter_instance, assert_distinct=True, **expected_kwargs):
    qs = _mock_qs()
    result = filter_instance.queryset(None, qs)
    qs.filter.assert_called_once_with(**expected_kwargs)
    if assert_distinct:
        qs.filter.return_value.distinct.assert_called_once()
        assert result is qs.filter.return_value.distinct.return_value
    else:
        assert result is qs.filter.return_value


def test_recurso_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(RecursoListFilter, admin_request))


def test_recurso_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(RecursoListFilter, admin_request, RECURSO_ID),
        associacao__periodos_iniciais__recurso_id=RECURSO_ID,
    )


def test_recurso_associacao_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(RecursoAssociacaoListFilter, admin_request))


def test_recurso_associacao_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(RecursoAssociacaoListFilter, admin_request, RECURSO_ID),
        periodos_iniciais__recurso_id=RECURSO_ID,
    )


def test_demonstrativo_financeiro_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(DemonstrativoFinanceiroListFilter, admin_request))


def test_demonstrativo_financeiro_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(DemonstrativoFinanceiroListFilter, admin_request, RECURSO_ID),
        prestacao_conta__periodo__recurso_id=RECURSO_ID,
    )


def test_relacao_bens_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(RelacaoBensListFilter, admin_request))


def test_relacao_bens_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(RelacaoBensListFilter, admin_request, RECURSO_ID),
        prestacao_conta__periodo__recurso_id=RECURSO_ID,
    )


def test_devolucao_prestacao_conta_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(DevolucaoPrestacaoContaFilter, admin_request))


def test_devolucao_prestacao_conta_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(DevolucaoPrestacaoContaFilter, admin_request, RECURSO_ID),
        prestacao_conta__periodo__recurso_id=RECURSO_ID,
    )


def test_analise_prestacao_conta_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(AnalisePrestacaoContaFilter, admin_request))


def test_analise_prestacao_conta_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(AnalisePrestacaoContaFilter, admin_request, RECURSO_ID),
        prestacao_conta__periodo__recurso_id=RECURSO_ID,
    )


def test_recurso_contas_associacao_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(RecursoContasAssociacaoListFilter, admin_request))


def test_recurso_contas_associacao_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(RecursoContasAssociacaoListFilter, admin_request, RECURSO_ID),
        tipo_conta__recurso_id=RECURSO_ID,
    )


def test_acao_associacao_a_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(AcaoAssociacaoAListFilter, admin_request))


def test_acao_associacao_a_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(AcaoAssociacaoAListFilter, admin_request, RECURSO_ID),
        acao__recurso_id=RECURSO_ID,
    )


def test_prestacao_conta_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(PrestacaoContaListFilter, admin_request))


def test_prestacao_conta_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(PrestacaoContaListFilter, admin_request, RECURSO_ID),
        periodo__recurso_id=RECURSO_ID,
    )


def test_periodo_recurso_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(PeriodoRecursoListFilter, admin_request))


def test_periodo_recurso_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(PeriodoRecursoListFilter, admin_request, RECURSO_ID),
        periodo__recurso_id=RECURSO_ID,
    )


def test_ata_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(AtaListFilter, admin_request))


def test_ata_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(AtaListFilter, admin_request, RECURSO_ID),
        assert_distinct=False,
        periodo__recurso_id=RECURSO_ID,
    )


def test_observacao_conciliacao_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(ObservacaoConciliacaoFilter, admin_request))


def test_observacao_conciliacao_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(ObservacaoConciliacaoFilter, admin_request, RECURSO_ID),
        periodo__recurso_id=RECURSO_ID,
    )


def test_analise_consolidado_dre_list_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(AnaliseConsolidadoDreListFilter, admin_request))


def test_analise_consolidado_dre_list_filter_queryset_com_valor(admin_request):
    _assert_filtered(
        make_filter(AnaliseConsolidadoDreListFilter, admin_request, RECURSO_ID),
        consolidado_dre__periodo__recurso_id=RECURSO_ID,
    )


# Testes dos filtros de DRE definidos diretamente em core/admin.py:
# DreListFilter (ComentarioAnalisePrestacaoAdmin) e DreArquivoDownloadFilter (ArquivoDownloadAdmin).
def _make_dre(codigo_eol, nome):
    dre = MagicMock()
    dre.codigo_eol = codigo_eol
    dre.nome = nome
    return dre


def test_dre_list_filter_title():
    assert DreListFilter.title == 'DRE'


def test_dre_list_filter_lookups_via_prestacao_conta(admin_request):
    dre = _make_dre('123456', 'DRE Teste')
    objeto = MagicMock()
    objeto.prestacao_conta.associacao.unidade.dre = dre
    objeto.associacao = None

    model_admin = MagicMock()
    model_admin.get_queryset.return_value = [objeto]

    filtro = make_filter(DreListFilter, admin_request, param_name='dre', model_admin=model_admin)

    assert ('123456', 'DRE Teste') in filtro.lookup_choices


def test_dre_list_filter_lookups_via_associacao(admin_request):
    dre = _make_dre('654321', 'DRE Associação')
    objeto = MagicMock()
    objeto.prestacao_conta = None
    objeto.associacao.unidade.dre = dre

    model_admin = MagicMock()
    model_admin.get_queryset.return_value = [objeto]

    filtro = make_filter(DreListFilter, admin_request, param_name='dre', model_admin=model_admin)

    assert ('654321', 'DRE Associação') in filtro.lookup_choices


def _dre_list_filter_model_admin_vazio():
    return MagicMock(get_queryset=lambda request: [])


# DreListFilter.queryset não retorna o queryset original quando não há valor
# (diferente dos demais filtros acima), então não reutiliza _assert_no_filter.
def test_dre_list_filter_queryset_sem_valor(admin_request):
    filtro = make_filter(
        DreListFilter, admin_request, param_name='dre', model_admin=_dre_list_filter_model_admin_vazio()
    )
    qs = _mock_qs()
    assert filtro.queryset(None, qs) is None
    qs.filter.assert_not_called()


def test_dre_list_filter_queryset_com_valor(admin_request):
    filtro = make_filter(
        DreListFilter, admin_request, RECURSO_ID, param_name='dre', model_admin=_dre_list_filter_model_admin_vazio()
    )
    qs = _mock_qs()
    filtro.queryset(None, qs)
    qs.filter.assert_called_once()


def test_dre_arquivo_download_filter_title():
    assert DreArquivoDownloadFilter.title == 'DRE'


def test_dre_arquivo_download_filter_lookups(dre, admin_request):
    filtro = DreArquivoDownloadFilter(admin_request, {}, ArquivoDownload, MagicMock())
    resultado = list(filtro.lookups(RequestFactory().get('/admin/'), None))
    assert any(nome == dre.nome for _, nome in resultado)


def test_dre_arquivo_download_filter_queryset_sem_valor(admin_request):
    _assert_no_filter(make_filter(DreArquivoDownloadFilter, admin_request, param_name='dre_filtro'))


def test_dre_arquivo_download_filter_queryset_com_valor(dre, admin_request):
    _assert_filtered(
        make_filter(DreArquivoDownloadFilter, admin_request, dre.codigo_eol, param_name='dre_filtro'),
        assert_distinct=False,
        dre__codigo_eol=dre.codigo_eol,
    )
