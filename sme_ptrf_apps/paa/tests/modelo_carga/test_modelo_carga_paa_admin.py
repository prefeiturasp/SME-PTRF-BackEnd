
def test_list_display(modelo_carga_paa_admin):
    assert modelo_carga_paa_admin.list_display == ('tipo_carga', 'arquivo')


def test_search_fields(modelo_carga_paa_admin):
    assert modelo_carga_paa_admin.search_fields == ('tipo_carga', )


def test_readonly_fields(modelo_carga_paa_admin):
    assert modelo_carga_paa_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
