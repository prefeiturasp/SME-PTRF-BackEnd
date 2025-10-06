
def test_list_display(objetivo_paa_admin):
    assert objetivo_paa_admin.list_display == ('nome', 'status')


def test_search_fields(objetivo_paa_admin):
    assert objetivo_paa_admin.search_fields == ('nome',)


def test_list_filter(objetivo_paa_admin):
    assert objetivo_paa_admin.list_filter == ('status',)


def test_readonly_fields(objetivo_paa_admin):
    assert objetivo_paa_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em',)


def test_raw_fields(objetivo_paa_admin):
    assert objetivo_paa_admin.raw_id_fields == ('paa',)
