
def test_list_display(recurso_proprios_paa_admin):
    assert recurso_proprios_paa_admin.list_display == ('fonte_recurso', 'associacao', 'data_prevista', 'descricao', 'valor',)


def test_search_fields(recurso_proprios_paa_admin):
    assert recurso_proprios_paa_admin.search_fields == ('fonte_recurso__nome', 'associacao__nome',)

def test_list_filter(recurso_proprios_paa_admin):
    assert recurso_proprios_paa_admin.list_filter == ('associacao',)
