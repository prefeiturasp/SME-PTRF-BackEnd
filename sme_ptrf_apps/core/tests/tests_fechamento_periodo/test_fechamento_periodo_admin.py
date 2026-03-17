from ...admin_filters import (
    PeriodoRecursoListFilter,
)


def test_fechamento_periodo_search_fields(fechamento_periodo_admin):
    assert fechamento_periodo_admin.search_fields == ('associacao__unidade__codigo_eol', 'associacao__nome',)


def test_fechamento_periodo_list_filter(fechamento_periodo_admin):
    assert fechamento_periodo_admin.list_filter == ('status', 'associacao', 'acao_associacao__acao',
                                                    'periodo', 'associacao__unidade__tipo_unidade',
                                                    'associacao__unidade__dre', 'conta_associacao__tipo_conta',
                                                    PeriodoRecursoListFilter)


def test_fechamento_periodo_list_display(fechamento_periodo_admin):
    assert fechamento_periodo_admin.list_display == ('get_eol_unidade', 'periodo', 'get_nome_acao',
                                                     'get_nome_conta', 'saldo_anterior', 'total_receitas',
                                                     'total_despesas', 'saldo_reprogramado', 'status')


def test_fechamento_periodo_readonly_fields(fechamento_periodo_admin):
    assert fechamento_periodo_admin.readonly_fields == ('saldo_reprogramado_capital',
                                                        'saldo_reprogramado_custeio',
                                                        'saldo_reprogramado_livre', 'uuid', 'id', 'criado_em')


def test_fechamento_periodo_list_display_links(fechamento_periodo_admin):
    assert fechamento_periodo_admin.list_display_links == ('periodo',)


def test_fechamento_periodo_raw_id_fields(fechamento_periodo_admin):
    assert fechamento_periodo_admin.raw_id_fields == ([
        'prestacao_conta',
        'periodo',
        'associacao',
        'conta_associacao',
        'acao_associacao',
        'fechamento_anterior']
    )
