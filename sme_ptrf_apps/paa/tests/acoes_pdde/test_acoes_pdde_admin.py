
def test_list_display(acao_pdde_admin):
    assert acao_pdde_admin.list_display == ('nome', 'programa')


def test_search_fields(acao_pdde_admin):
    assert acao_pdde_admin.search_fields == ('nome', 'programa__nome')


def test_list_filter(acao_pdde_admin):
    assert acao_pdde_admin.list_filter == ('programa',)


def test_readonly_fields(acao_pdde_admin):
    assert acao_pdde_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')
