from rangefilter.filters import DateRangeFilter
from ...admin_filters import (
    RecursoContasAssociacaoListFilter,
)


# Testes Conta Associação Admin
def test_conta_associacao_search_fields(conta_associacao_admin):
    assert conta_associacao_admin.search_fields == ('uuid', 'associacao__unidade__codigo_eol',
                                                    'associacao__unidade__nome', 'associacao__nome')


def test_conta_associacao_list_filter(conta_associacao_admin):
    assert conta_associacao_admin.list_filter == ('status', 'tipo_conta', 'associacao__unidade__tipo_unidade',
                                                  'associacao__unidade__dre', ('data_inicio', DateRangeFilter),
                                                  RecursoContasAssociacaoListFilter)


def test_conta_associacao_list_display(conta_associacao_admin):
    assert conta_associacao_admin.list_display == ('associacao', 'tipo_conta', 'status', 'data_inicio')


def test_conta_associacao_readonly_fields(conta_associacao_admin):
    assert conta_associacao_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_conta_associacao_raw_id_fields(conta_associacao_admin):
    assert conta_associacao_admin.raw_id_fields == ('associacao',)
