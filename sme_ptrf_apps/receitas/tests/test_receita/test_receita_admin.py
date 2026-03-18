from ...admin_filters import (
    ReceitaFilter,
)


def test_receita_admin_search_fields(receita_admin):
    assert receita_admin.search_fields == (
        'detalhe_tipo_receita__nome',
        'detalhe_outros',
        'associacao__nome',
        'associacao__unidade__nome',
        'associacao__unidade__codigo_eol'
    )


def test_receita_admin_list_filter(receita_admin):
    filters = receita_admin.list_filter

    expected_fields_tuple = [
        'conferido',
        'data',
        'associacao__unidade__dre',
        'acao_associacao__acao__nome',
        'conta_associacao__tipo_conta__nome',
        'tipo_receita',
    ]

    fields_tuple = [f[0] for f in filters if isinstance(f, tuple)]

    for field in expected_fields_tuple:
        assert field in fields_tuple

    fields = [f for f in filters if isinstance(f, str)]

    fields_str_expected = [
        'categoria_receita',
        'status',
    ]

    for field in fields_str_expected:
        assert field in fields

    assert filters[-1] is ReceitaFilter


def test_receita_admin_list_display(receita_admin):
    assert receita_admin.list_display == ('data', 'valor', 'categoria_receita', 'detalhamento', 'associacao', 'repasse',
                                          'status')


def test_receita_admin_readonly_fields(receita_admin):
    assert receita_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_receita_admin_raw_id_fields(receita_admin):
    assert receita_admin.raw_id_fields == (
        'associacao',
        'conta_associacao',
        'acao_associacao',
        'tipo_receita',
        'repasse',
        'detalhe_tipo_receita',
        'referencia_devolucao',
        'periodo_conciliacao',
        'saida_do_recurso',
        'rateio_estornado',
    )
