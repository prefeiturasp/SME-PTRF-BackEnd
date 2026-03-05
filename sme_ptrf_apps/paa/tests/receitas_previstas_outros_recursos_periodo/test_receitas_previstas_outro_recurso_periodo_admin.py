
def test_list_display(receitas_previstas_outros_recursos_periodo_admin):
    assert receitas_previstas_outros_recursos_periodo_admin.list_display == (
        'outro_recurso_periodo', 'previsao_valor_custeio', 'previsao_valor_capital', 'previsao_valor_livre',
        'unidade_nome'
    )


def test_search_fields(receitas_previstas_outros_recursos_periodo_admin):
    assert receitas_previstas_outros_recursos_periodo_admin.search_fields == (
        'outro_recurso_periodo__outro_recurso__nome', 'outro_recurso_periodo__periodo_paa__referencia')


def test_raw_id_fields(receitas_previstas_outros_recursos_periodo_admin):
    assert receitas_previstas_outros_recursos_periodo_admin.raw_id_fields == ('outro_recurso_periodo', 'paa')


def test_list_filter(receitas_previstas_outros_recursos_periodo_admin):
    assert receitas_previstas_outros_recursos_periodo_admin.list_filter == (
        'outro_recurso_periodo__outro_recurso', 'paa', 'paa__associacao')


def test_readonly_fields(receitas_previstas_outros_recursos_periodo_admin):
    assert receitas_previstas_outros_recursos_periodo_admin.readonly_fields == (
        'uuid', 'id', 'criado_em', 'alterado_em')
