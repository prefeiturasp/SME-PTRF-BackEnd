from ...admin_filters import (
    RepasseFilter,
)


def test_receita_admin_search_fields(repasse_admin):
    assert repasse_admin.search_fields == ('associacao__nome', 'associacao__unidade__codigo_eol',
                                           'carga_origem_linha_id')


def test_repasse_admin_list_filter(repasse_admin):
    assert repasse_admin.list_filter == ('periodo', 'status', 'carga_origem', 'associacao__unidade__dre', RepasseFilter)


def test_repasse_admin_list_display(repasse_admin):
    assert repasse_admin.list_display == ('associacao', 'periodo', 'valor_capital', 'valor_custeio',
                                          'valor_livre', 'tipo_conta', 'acao', 'status')


def test_repasse_admin_readonly_fields(repasse_admin):
    assert repasse_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_repasse_admin_raw_id_fields(repasse_admin):
    assert repasse_admin.raw_id_fields == ('associacao', 'periodo', 'conta_associacao', 'acao_associacao',
                                           'carga_origem')
