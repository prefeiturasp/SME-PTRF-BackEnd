
def test_list_display(categoria_pdde_admin):
    assert categoria_pdde_admin.list_display == ('nome',)


def test_search_fields(categoria_pdde_admin):
    assert categoria_pdde_admin.search_fields == ('nome',)


def test_list_filter(categoria_pdde_admin):
    assert categoria_pdde_admin.list_filter == ('nome',)


def test_readonly_fields(categoria_pdde_admin):
    assert categoria_pdde_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
