
def test_list_display(prioridade_paa_admin):
    assert prioridade_paa_admin.list_display == (
        'nome',
        'prioridade',
        'recurso',
        'tipo_aplicacao',
        'programa_pdde',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total',
        'paa',
    )


def test_search_fields(prioridade_paa_admin):
    assert prioridade_paa_admin.search_fields == (
        'acao_associacao__acao__nome', 'acao_associacao__associacao__nome', 'programa_pdde__nome',
        'acao_pdde__nome', 'tipo_despesa_custeio__nome', 'especificacao_material__descricao')


def test_list_filter(prioridade_paa_admin):
    assert prioridade_paa_admin.list_filter == (
        'recurso', 'prioridade', 'tipo_aplicacao', 'programa_pdde', 'acao_pdde', 'paa')


def test_readonly_fields(prioridade_paa_admin):
    assert prioridade_paa_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_raw_fields(prioridade_paa_admin):
    assert prioridade_paa_admin.raw_id_fields == (
        'paa', 'acao_pdde', 'acao_associacao', 'programa_pdde', 'tipo_despesa_custeio', 'especificacao_material')
