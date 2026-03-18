from ...admin_filters import (
    DespesaFilter,
)
from ...admin import PeriodoDaDespesaFilter


def test_despesas_search_fields(despesas_admin):
    assert despesas_admin.search_fields == (
        'numero_documento',
        'nome_fornecedor',
        'documento_transacao',
        'associacao__nome',
        'associacao__unidade__codigo_eol',
        'recurso__nome'
    )


def test_despesas_list_filter(despesas_admin):
    filtros = despesas_admin.list_filter

    campos_tupla = [f[0] for f in filtros if isinstance(f, tuple)]

    campos_tupla_esperados = [
        'recurso__nome_exibicao',
        'data_documento',
        'data_transacao',
    ]

    for campo in campos_tupla_esperados:
        assert campo in campos_tupla

    campos_string = [f for f in filtros if isinstance(f, str)]

    campos_string_esperados = [
        'associacao',
        'associacao__unidade__dre',
        'associacao__unidade__tipo_unidade',
        'status',
        'nome_fornecedor',
        'tipo_documento',
        'tipo_transacao',
        'eh_despesa_sem_comprovacao_fiscal',
        'eh_despesa_reconhecida_pela_associacao',
        'retem_imposto',
        'despesa_anterior_ao_uso_do_sistema',
        'despesa_anterior_ao_uso_do_sistema_pc_concluida',
    ]

    for campo in campos_string_esperados:
        assert campo in campos_string

    filtros_classes = [f for f in filtros if isinstance(f, type)]

    filtros_classes_esperados = [
        PeriodoDaDespesaFilter,
        DespesaFilter,
    ]

    for filtro in filtros_classes_esperados:
        assert filtro in filtros_classes


def test_despesas_list_display(despesas_admin):
    assert despesas_admin.list_display == (
        'tipo_documento', 'numero_documento', 'data_documento', 'nome_fornecedor', 'valor_total', 'status',
        'associacao', 'retem_imposto', 'despesa_anterior_ao_uso_do_sistema',
        'despesa_anterior_ao_uso_do_sistema_pc_concluida', 'recurso')


def test_despesas_readonly_fields(despesas_admin):
    assert despesas_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em', 'recurso')


def test_despesas_filter_horizontal(despesas_admin):
    assert despesas_admin.filter_horizontal == ('despesas_impostos', 'motivos_pagamento_antecipado')
