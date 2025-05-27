
def test_list_display(receitas_previstas_pdde_admin):
    assert receitas_previstas_pdde_admin.list_display == (
        'paa',
        'acao_pdde',
        'previsao_valor_custeio',
        'previsao_valor_capital',
        'previsao_valor_livre',
        'saldo_custeio',
        'saldo_capital',
        'saldo_livre'
    )


def test_list_filter_fields(receitas_previstas_pdde_admin):
    assert receitas_previstas_pdde_admin.list_filter == ('acao_pdde', 'acao_pdde__programa')


def test_raw_id_fields(receitas_previstas_pdde_admin):
    assert receitas_previstas_pdde_admin.raw_id_fields == ('paa', 'acao_pdde')


def test_readonly_fields(receitas_previstas_pdde_admin):
    assert receitas_previstas_pdde_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
