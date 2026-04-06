from ...admin_filters import (
    AcaoAssociacaoAListFilter
)


# Testes Ação Associação Admin
def test_acao_associacao_search_fields(acao_associacao_admin):
    assert acao_associacao_admin.search_fields == ('uuid', 'associacao__unidade__codigo_eol',
                                                   'associacao__unidade__nome', 'associacao__nome')


def test_acao_associacao_list_filter(acao_associacao_admin):
    assert acao_associacao_admin.list_filter == ('status', 'acao', 'associacao__unidade__tipo_unidade',
                                                 'associacao__unidade__dre', AcaoAssociacaoAListFilter,
                                                 'acao__aceita_custeio', 'acao__aceita_capital', 'acao__aceita_livre',
                                                 'acao__exibir_paa')


def test_acao_ssociacao_list_display(acao_associacao_admin):
    assert acao_associacao_admin.list_display == ('associacao', 'acao', 'status', 'criado_em')


def test_acao_associacao_readonly_fields(acao_associacao_admin):
    assert acao_associacao_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_acao_ssociacao_raw_id_fields(acao_associacao_admin):
    assert acao_associacao_admin.raw_id_fields == ('associacao',)
