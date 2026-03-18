from ...admin_filters import (
    AnalisePrestacaoContaFilter,
)


def test_analise_prestacao_conta_search_fields(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.search_fields == ('prestacao_conta__associacao__unidade__codigo_eol',
                                                           'prestacao_conta__associacao__unidade__nome',
                                                           'prestacao_conta__associacao__nome')


def test_analise_prestacao_conta_list_filter(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.list_filter == (
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__tipo_unidade',
        'prestacao_conta__associacao__unidade__dre',
        'status',
        'status_versao',
        'versao',
        'status_versao_apresentacao_apos_acertos',
        'versao_pdf_apresentacao_apos_acertos',
        AnalisePrestacaoContaFilter,
    )


def test_analise_prestacao_conta_list_display(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.list_display == ('get_unidade', 'get_referencia_periodo', 'criado_em',
                                                          'status',)


def test_analise_prestacao_conta_readonly_fields(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_analise_prestacao_conta_list_display_links(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.list_display_links == ('get_unidade',)


def test_analise_prestacao_conta_raw_id_fields(analise_prestacao_conta_admin):
    assert analise_prestacao_conta_admin.raw_id_fields == (['prestacao_conta', 'devolucao_prestacao_conta', ])
