def test_list_display(bem_produzido_admin):
    assert bem_produzido_admin.list_display == [
        'id',
        'status',
        'especificacao_do_bem',
        'num_processo_incorporacao',
        'quantidade',
        'valor_individual',
    ]

def test_raw_id_fields(bem_produzido_admin):
    assert bem_produzido_admin.raw_id_fields == ('especificacao_do_bem','associacao')