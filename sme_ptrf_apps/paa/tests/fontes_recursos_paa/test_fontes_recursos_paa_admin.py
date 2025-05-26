
def test_list_display(fonte_recurso_paa_admin):
    assert fonte_recurso_paa_admin.list_display == ('nome',)


def test_search_fields(fonte_recurso_paa_admin):
    assert fonte_recurso_paa_admin.search_fields == ('nome',)
