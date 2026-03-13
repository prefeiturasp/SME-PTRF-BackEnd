from ...admin_filters import (
    RateioDespesaFilter,
)


def test_rateio_despesas_search_fields(rateio_despesas_admin):
    assert rateio_despesas_admin.search_fields == (
        'despesa__numero_documento', 'despesa__nome_fornecedor', 'especificacao_material_servico__descricao',
        'associacao__unidade__codigo_eol', 'associacao__unidade__nome',)


def test_rateio_despesas_list_filter(rateio_despesas_admin):
    filters = rateio_despesas_admin.list_filter

    expected_fields = [
        'conferido',
        'tag',
        'associacao__unidade__dre',
        'acao_associacao__acao__nome',
        'conta_associacao__tipo_conta__nome',
        'aplicacao_recurso',
        'tipo_custeio',
        'despesa__tipo_documento',
        'despesa__tipo_transacao',
    ]

    fields = [f[0] for f in filters if isinstance(f, tuple)]

    for field in expected_fields:
        assert field in fields

    assert filters[-1] is RateioDespesaFilter


def test_rateio_despesas_list_display(rateio_despesas_admin):
    assert rateio_despesas_admin.list_display == (
        "uuid", 'numero_documento', 'associacao', 'acao', 'valor_rateio', 'quantidade_itens_capital', 'status',)


def test_rateio_despesas_readonly_fields(rateio_despesas_admin):
    assert rateio_despesas_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_rateio_despesas_raw_id_fields(rateio_despesas_admin):
    assert rateio_despesas_admin.raw_id_fields == ('despesa', 'associacao', 'acao_associacao', 'conta_associacao',
                                                   'especificacao_material_servico')
