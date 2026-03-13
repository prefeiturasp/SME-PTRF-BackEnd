from ...admin_filters import (
    RelacaoBensListFilter,
)


def test_relacao_bens_search_fields(relacao_bens_admin):
    assert relacao_bens_admin.search_fields == (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )


def test_relacao_bens_list_filter(relacao_bens_admin):
    assert relacao_bens_admin.list_filter == (
        'prestacao_conta__associacao',
        'conta_associacao__tipo_conta',
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__dre',
        'periodo_previa',
        'versao',
        'status',
        RelacaoBensListFilter
    )


def test_relacao_bens_list_display(relacao_bens_admin):
    assert relacao_bens_admin.list_display == (
        'get_nome_associacao',
        'get_periodo',
        'get_nome_conta',
        'get_nome_dre',
        'criado_em',
        'versao',
        'status'
    )


def test_relacao_bens_readonly_fields(relacao_bens_admin):
    assert relacao_bens_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_relacao_bens_list_display_links(relacao_bens_admin):
    assert relacao_bens_admin.list_display_links == ('get_nome_associacao',)


def test_relacao_bens_autocomplete_fields(relacao_bens_admin):
    assert relacao_bens_admin.autocomplete_fields == (['conta_associacao', 'periodo_previa', 'prestacao_conta'])
