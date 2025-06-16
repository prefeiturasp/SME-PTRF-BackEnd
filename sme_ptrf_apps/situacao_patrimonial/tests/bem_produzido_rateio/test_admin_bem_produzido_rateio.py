def test_list_display(bem_produzido_rateio_admin):
    assert bem_produzido_rateio_admin.list_display == [
        '__str__',
        'id',
        'rateio',
    ]

def test_raw_id_fields(bem_produzido_rateio_admin):
    assert bem_produzido_rateio_admin.raw_id_fields == (
        'rateio',
        'bem_produzido_despesa'
    )

def test_readonly_fields(bem_produzido_rateio_admin):
    assert bem_produzido_rateio_admin.readonly_fields == (
        'uuid',
        'id',
        'criado_em',
        'alterado_em'
    )