
def test_list_display(outros_recursos_periodo_admin):
    assert outros_recursos_periodo_admin.list_display == ('periodo_paa', 'outro_recurso', 'ativo')


def test_search_fields(outros_recursos_periodo_admin):
    assert outros_recursos_periodo_admin.search_fields == ('periodo_paa__referencia', 'outro_recurso__nome')


def test_readonly_fields(outros_recursos_periodo_admin):
    assert outros_recursos_periodo_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_raw_id_fields(outros_recursos_periodo_admin):
    assert outros_recursos_periodo_admin.raw_id_fields == ('periodo_paa', 'outro_recurso')


def test_filter_horizontal(outros_recursos_periodo_admin):
    assert outros_recursos_periodo_admin.filter_horizontal == ('unidades',)
