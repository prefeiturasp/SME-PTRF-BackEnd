from rangefilter.filters import DateRangeFilter


def test_list_display(periodo_paa_admin):
    assert periodo_paa_admin.list_display == ('id', 'referencia', 'data_inicial', 'data_final',)


def test_search_fields(periodo_paa_admin):
    assert periodo_paa_admin.search_fields == ('referencia',)


def test_list_filter(periodo_paa_admin):
    assert periodo_paa_admin.list_filter == (('data_inicial', DateRangeFilter), ('data_final', DateRangeFilter),)
