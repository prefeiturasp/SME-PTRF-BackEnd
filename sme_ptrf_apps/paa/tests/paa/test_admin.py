
def test_list_display(paa_admin):
    assert paa_admin.list_display == ('periodo_paa', 'associacao', 'status', 'status_andamento')


def test_list_display_links(paa_admin):
    assert paa_admin.list_display_links == ['periodo_paa']


def test_raw_id_fields(paa_admin):
    assert paa_admin.raw_id_fields == ['periodo_paa', 'associacao']
