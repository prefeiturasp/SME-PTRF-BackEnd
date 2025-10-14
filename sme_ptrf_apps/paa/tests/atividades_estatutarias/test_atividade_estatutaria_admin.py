
def test_list_display(atividade_estatutaria_admin):
    assert atividade_estatutaria_admin.list_display == ('nome', 'status', 'mes', 'tipo')


def test_search_fields(atividade_estatutaria_admin):
    assert atividade_estatutaria_admin.search_fields == ('nome',)


def test_list_filter(atividade_estatutaria_admin):
    assert atividade_estatutaria_admin.list_filter == ('status', 'mes', 'tipo')


def test_readonly_fields(atividade_estatutaria_admin):
    assert atividade_estatutaria_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em',)
