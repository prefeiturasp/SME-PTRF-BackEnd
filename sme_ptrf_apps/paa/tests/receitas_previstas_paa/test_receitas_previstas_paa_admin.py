
def test_list_display(receitas_previstas_paa_admin):
    assert receitas_previstas_paa_admin.list_display == (
        'acao_associacao', 'previsao_valor_custeio', 'previsao_valor_capital', 'previsao_valor_livre'
    )


def test_search_fields(receitas_previstas_paa_admin):
    assert receitas_previstas_paa_admin.search_fields == (
        'acao_associacao__acao__nome', 'acao_associacao__associacao__nome'
    )


def test_raw_id_fields(receitas_previstas_paa_admin):
    assert receitas_previstas_paa_admin.raw_id_fields == ('acao_associacao', 'paa')


def test_list_filter(receitas_previstas_paa_admin):
    assert receitas_previstas_paa_admin.list_filter == ('acao_associacao__associacao', 'paa')


def test_readonly_fields(receitas_previstas_paa_admin):
    assert receitas_previstas_paa_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
