
def test_list_display(programa_pdde_admin):
    assert programa_pdde_admin.list_display == ('nome',)


def test_search_fields(programa_pdde_admin):
    assert programa_pdde_admin.search_fields == ('nome',)


def test_list_filter(programa_pdde_admin):
    assert programa_pdde_admin.list_filter == ('nome',)


def test_readonly_fields(programa_pdde_admin):
    assert programa_pdde_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
