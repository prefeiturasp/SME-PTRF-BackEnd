
def test_list_display(documento_paa_admin):
    assert documento_paa_admin.list_display == ('paa', 'status_geracao', 'versao', 'criado_em', 'alterado_em')


def test_search_fields(documento_paa_admin):
    assert documento_paa_admin.search_fields == ('paa__associacao__nome', 'paa__associacao__unidade__codigo_eol')


def test_readonly_fields(documento_paa_admin):
    assert documento_paa_admin.readonly_fields == ('uuid', 'id', 'criado_em',)


def test_raw_id_fields(documento_paa_admin):
    assert documento_paa_admin.raw_id_fields == ('paa',)


def test_list_filter(documento_paa_admin):
    assert documento_paa_admin.list_filter == ('status_geracao', 'versao', 'paa__periodo_paa')
