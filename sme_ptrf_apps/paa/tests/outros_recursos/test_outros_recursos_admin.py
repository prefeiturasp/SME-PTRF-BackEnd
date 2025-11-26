
def test_list_display(outros_recursos_admin):
    assert outros_recursos_admin.list_display == ('nome', 'aceita_capital', 'aceita_custeio', 'aceita_livre_aplicacao')


def test_search_fields(outros_recursos_admin):
    assert outros_recursos_admin.search_fields == ('nome', )


def test_readonly_fields(outros_recursos_admin):
    assert outros_recursos_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
