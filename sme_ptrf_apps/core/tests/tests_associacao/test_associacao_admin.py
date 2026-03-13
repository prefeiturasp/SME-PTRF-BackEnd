from rangefilter.filters import DateRangeFilter
from ...admin_filters import (
    RecursoAssociacaoListFilter,
)


# Testes Associação Admin
def test_associacao_search_fields(associacao_admin):
    assert associacao_admin.search_fields == ('uuid', 'nome', 'cnpj', 'unidade__nome', 'unidade__codigo_eol', )


def test_associacao_list_filter(associacao_admin):
    assert associacao_admin.list_filter == (
        'unidade__dre',
        'periodo_inicial',
        'unidade__tipo_unidade',
        ('data_de_encerramento', DateRangeFilter),
        'migrada_para_historico_de_membros',
        RecursoAssociacaoListFilter,
    )


def test_associacao_list_display(associacao_admin):
    assert associacao_admin.list_display == ('nome', 'cnpj', 'get_nome_escola',
                                             'get_periodo_inicial_referencia', 'data_de_encerramento',
                                             'migrada_para_historico_de_membros')


def test_associacao_readonly_fields(associacao_admin):
    assert associacao_admin.readonly_fields == ('uuid', 'id')


def test_associacao_list_display_links(associacao_admin):
    assert associacao_admin.list_display_links == ('nome', 'cnpj')
