def test_list_display(bem_produzido_despesa_admin):
    assert bem_produzido_despesa_admin.list_display == [
        '__str__',
        'id',
        'despesa',
    ]

def test_raw_id_fields(bem_produzido_despesa_admin):
    assert bem_produzido_despesa_admin.raw_id_fields == (
        'despesa',
        'bem_produzido'
    )

def test_readonly_fields(bem_produzido_despesa_admin):
    assert bem_produzido_despesa_admin.readonly_fields == (
        'uuid',
        'id',
        'criado_em',
        'alterado_em'
    )