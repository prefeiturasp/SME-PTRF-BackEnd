def test_list_display(bem_produzido_admin):
    assert bem_produzido_admin.list_display == [
        '__str__',
        'status',
        'especificacao_do_bem',
        'num_processo_incorporacao',
        'quantidade',
        'valor_individual',
    ]

def test_raw_id_fields(bem_produzido_admin):
    assert bem_produzido_admin.raw_id_fields == ('especificacao_do_bem','associacao')

def test_readonly_fields(bem_produzido_despesa_admin):
    assert bem_produzido_despesa_admin.readonly_fields == (
        'uuid',
        'id',
        'criado_em',
        'alterado_em'
    )