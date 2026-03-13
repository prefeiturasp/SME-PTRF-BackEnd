from ...admin_filters import (
    PrestacaoContaListFilter,
)


def test_conta_associacao_search_fields(prestacao_conta_admin):
    assert prestacao_conta_admin.search_fields == ('associacao__unidade__codigo_eol', 'associacao__nome',
                                                   'associacao__unidade__nome')


def test_conta_associacao_list_filter(prestacao_conta_admin):
    assert prestacao_conta_admin.list_filter == (
        'status',
        'associacao__unidade__dre',
        'associacao',
        'periodo',
        'publicada',
        'consolidado_dre__sequencia_de_publicacao',
        'consolidado_dre__id',
        'associacao__unidade__tipo_unidade',
        PrestacaoContaListFilter
    )


def test_conta_associacao_list_display(prestacao_conta_admin):
    assert prestacao_conta_admin.list_display == (
        'get_eol_unidade',
        'get_nome_unidade',
        'associacao',
        'get_periodo_referencia',
        'status',
        'publicada',
        'get_relatorio_referencia'
    )


def test_conta_associacao_readonly_fields(prestacao_conta_admin):
    assert prestacao_conta_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_conta_associacao_list_display_links(prestacao_conta_admin):
    assert prestacao_conta_admin.list_display_links == ('get_nome_unidade',)


def test_conta_associacao_raw_id_fields(prestacao_conta_admin):
    assert prestacao_conta_admin.raw_id_fields == ('periodo', 'associacao', 'analise_atual', 'consolidado_dre',)
