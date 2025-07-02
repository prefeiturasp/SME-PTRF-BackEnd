def test_list_display(bem_produzido_admin):
    assert bem_produzido_admin.list_display == [
        '__str__',
        'status'
    ]

def test_raw_id_fields(bem_produzido_admin):
    assert bem_produzido_admin.raw_id_fields == ('associacao',)

def test_readonly_fields(bem_produzido_despesa_admin):
    assert bem_produzido_despesa_admin.readonly_fields == (
        'uuid',
        'id',
        'criado_em',
        'alterado_em'
    )