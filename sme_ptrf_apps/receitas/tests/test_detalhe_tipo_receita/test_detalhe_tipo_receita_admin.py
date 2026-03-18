from ...admin_filters import (
    DetalheTipoReceitaFilter,
)


def test_detalhe_tipo_receita_search_fields(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.search_fields == ('nome',)


def test_detalhe_tipo_receita_list_filter(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.list_filter == ('tipo_receita', DetalheTipoReceitaFilter)


def test_detalhe_tipo_receita_list_display(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.list_display == ('nome', 'tipo_receita')


def test_detalhe_tipo_receita_readonly_fields(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.readonly_fields == ('uuid', 'id')
