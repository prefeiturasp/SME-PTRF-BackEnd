from rangefilter.filters import DateRangeFilter
from ...admin_filters import (
    DemonstrativoFinanceiroListFilter,
)


def test_demonstrativo_financeiro_search_fields(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.search_fields == (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )


def test_demonstrativo_financeiro_list_filter(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.list_filter == (
        'prestacao_conta__associacao',
        'conta_associacao__tipo_conta',
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__dre',
        'periodo_previa',
        'status',
        'versao',
        ('criado_em', DateRangeFilter),
        'arquivo_pdf_regerado',
        DemonstrativoFinanceiroListFilter
    )


def test_demonstrativo_financeiro_list_display(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.list_display == (
        'get_nome_associacao',
        'get_periodo',
        'get_nome_conta',
        'get_nome_dre',
        'criado_em',
        'versao',
        'status',
    )


def test_demonstrativo_financeiro_readonly_fields(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_demonstrativo_financeiro_list_display_links(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.list_display_links == ('get_nome_associacao',)


def test_demonstrativo_financeiro_autocomplete_fields(demonstrativo_financeiro_admin):
    assert demonstrativo_financeiro_admin.autocomplete_fields == (['conta_associacao', 'periodo_previa',
                                                                   'prestacao_conta'])
