from unittest.mock import MagicMock
from django.test import RequestFactory
from django.contrib.admin.sites import AdminSite

from sme_ptrf_apps.receitas.admin import RecursoFilter
from sme_ptrf_apps.receitas.models.receita import Receita
from ...admin_filters import (
    ReceitaFilter,
)


def test_receita_admin_search_fields(receita_admin):
    assert receita_admin.search_fields == (
        'detalhe_tipo_receita__nome',
        'detalhe_outros',
        'associacao__nome',
        'associacao__unidade__nome',
        'associacao__unidade__codigo_eol'
    )


def test_receita_admin_list_filter(receita_admin):
    filters = receita_admin.list_filter

    expected_fields_tuple = [
        'conferido',
        'data',
        'associacao__unidade__dre',
        'acao_associacao__acao__nome',
        'conta_associacao__tipo_conta__nome',
        'tipo_receita',
    ]

    fields_tuple = [f[0] for f in filters if isinstance(f, tuple)]

    for field in expected_fields_tuple:
        assert field in fields_tuple

    fields = [f for f in filters if isinstance(f, str)]

    fields_str_expected = [
        'categoria_receita',
        'status',
    ]

    for field in fields_str_expected:
        assert field in fields

    assert filters[-1] is ReceitaFilter


def test_receita_admin_list_display(receita_admin):
    assert receita_admin.list_display == ('data', 'valor', 'categoria_receita', 'detalhamento', 'associacao', 'repasse',
                                          'status')


def test_receita_admin_readonly_fields(receita_admin):
    assert receita_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_receita_admin_raw_id_fields(receita_admin):
    assert receita_admin.raw_id_fields == (
        'associacao',
        'conta_associacao',
        'acao_associacao',
        'tipo_receita',
        'repasse',
        'detalhe_tipo_receita',
        'referencia_devolucao',
        'periodo_conciliacao',
        'saida_do_recurso',
        'rateio_estornado',
    )


def test_receita_admin_ordering(receita_admin):
    assert receita_admin.ordering == ('-data',)


def test_receita_admin_actions(receita_admin):
    assert 'conciliar_receita' in receita_admin.actions
    assert 'desconciliar_receita' in receita_admin.actions


def test_conciliar_receita_action(receita_admin, receita_2020_1_role_repasse_capital_nao_conferida):
    request = MagicMock()
    queryset = Receita.objects.filter(pk=receita_2020_1_role_repasse_capital_nao_conferida.pk)
    receita_admin.conciliar_receita(request, queryset)
    receita_2020_1_role_repasse_capital_nao_conferida.refresh_from_db()
    assert receita_2020_1_role_repasse_capital_nao_conferida.conferido is True


def test_desconciliar_receita_action(receita_admin, receita_2020_1_role_repasse_capital_conferida):
    request = MagicMock()
    queryset = Receita.objects.filter(pk=receita_2020_1_role_repasse_capital_conferida.pk)
    receita_admin.desconciliar_receita(request, queryset)
    receita_2020_1_role_repasse_capital_conferida.refresh_from_db()
    assert receita_2020_1_role_repasse_capital_conferida.conferido is False


def _make_recurso_filter(value=None):
    request = RequestFactory().get('/admin/')
    params = {'recurso': str(value)} if value is not None else {}
    return RecursoFilter(request, params, Receita, AdminSite())


def test_recurso_filter_title():
    assert RecursoFilter.title == 'Recurso'


def test_recurso_filter_parameter_name():
    assert RecursoFilter.parameter_name == 'recurso'


def test_recurso_filter_lookups_retorna_recursos(recurso_legado):
    filtro = _make_recurso_filter()
    resultado = list(filtro.lookups(RequestFactory().get('/admin/'), None))
    assert any(nome == recurso_legado.nome for _, nome in resultado)


def test_recurso_filter_queryset_sem_valor():
    filtro = _make_recurso_filter()
    qs = MagicMock()
    resultado = filtro.queryset(None, qs)
    assert resultado is qs
    qs.filter.assert_not_called()


def test_recurso_filter_queryset_com_valor(recurso_legado):
    filtro = _make_recurso_filter(str(recurso_legado.uuid))
    qs = MagicMock()
    filtro.queryset(None, qs)
    qs.filter.assert_called_once_with(recurso__uuid=str(recurso_legado.uuid))
