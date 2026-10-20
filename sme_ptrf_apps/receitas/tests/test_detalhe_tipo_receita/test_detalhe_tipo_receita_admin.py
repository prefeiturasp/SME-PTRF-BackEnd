from unittest.mock import MagicMock, patch

from ...admin_filters import (
    DetalheTipoReceitaFilter,
)


def test_detalhe_tipo_receita_search_fields(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.search_fields == ('nome',)


def test_detalhe_tipo_receita_list_filter(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.list_filter == ('tipo_receita', DetalheTipoReceitaFilter)


def test_detalhe_tipo_receita_list_display(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.list_display == ('nome', 'tipo_receita', 'recurso')


def test_detalhe_tipo_receita_readonly_fields(detalhe_tipo_receita_admin):
    assert detalhe_tipo_receita_admin.readonly_fields == ('uuid', 'id')


def test_recurso_display_com_tipo_receita(detalhe_tipo_receita_admin, detalhe_tipo_receita):
    resultado = detalhe_tipo_receita_admin.recurso(detalhe_tipo_receita)
    assert resultado == detalhe_tipo_receita.tipo_receita.recurso


def test_recurso_display_sem_tipo_receita(detalhe_tipo_receita_admin):
    obj = MagicMock()
    obj.tipo_receita = None
    resultado = detalhe_tipo_receita_admin.recurso(obj)
    assert resultado is None


def test_get_queryset_retorna_detalhe(detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita):
    qs = detalhe_tipo_receita_admin.get_queryset(admin_request)
    assert detalhe_tipo_receita in qs


def test_get_readonly_fields_sem_obj(detalhe_tipo_receita_admin, admin_request):
    fields = detalhe_tipo_receita_admin.get_readonly_fields(admin_request)
    assert fields == ('uuid', 'id')
    assert 'tipo_receita' not in fields


def test_get_readonly_fields_obj_sem_receitas(
        detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita_parametrizacao):
    fields = detalhe_tipo_receita_admin.get_readonly_fields(admin_request, obj=detalhe_tipo_receita_parametrizacao)
    assert 'tipo_receita' not in fields


def test_get_readonly_fields_obj_com_receitas(
        detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita_parametrizacao_com_receita):
    fields = detalhe_tipo_receita_admin.get_readonly_fields(
        admin_request, obj=detalhe_tipo_receita_parametrizacao_com_receita)
    assert 'tipo_receita' in fields


def test_change_view_warning_quando_tem_receitas(
        detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita_parametrizacao_com_receita):
    with patch('django.contrib.admin.ModelAdmin.change_view', return_value=MagicMock()):
        with patch('sme_ptrf_apps.receitas.admin.messages.warning') as mock_warning:
            detalhe_tipo_receita_admin.change_view(
                admin_request, str(detalhe_tipo_receita_parametrizacao_com_receita.pk)
            )
    mock_warning.assert_called_once()
    assert 'Tipo de Receita' in mock_warning.call_args[0][1]


def test_change_view_sem_warning_quando_sem_receitas(
        detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita_parametrizacao):
    with patch('django.contrib.admin.ModelAdmin.change_view', return_value=MagicMock()):
        with patch('sme_ptrf_apps.receitas.admin.messages.warning') as mock_warning:
            detalhe_tipo_receita_admin.change_view(
                admin_request, str(detalhe_tipo_receita_parametrizacao.pk)
            )
    mock_warning.assert_not_called()


def test_form_clean_sem_tipo_receita_levanta_erro(detalhe_tipo_receita_admin, admin_request):
    form_class = detalhe_tipo_receita_admin.get_form(admin_request)
    form = form_class(data={'nome': 'Qualquer Nome', 'tipo_receita': ''})
    assert not form.is_valid()
    assert any('Tipo de Receita é obrigatório' in e for e in form.non_field_errors())


def test_form_recusa_tipo_receita_sem_detalhamento(
        detalhe_tipo_receita_admin, admin_request, tipo_receita_sem_detalhamento):
    # O queryset do campo tipo_receita já filtra para possui_detalhamento=True,
    # portanto submeter um tipo sem detalhamento resulta em erro de campo.
    form_class = detalhe_tipo_receita_admin.get_form(admin_request)
    form = form_class(data={'nome': 'Qualquer Nome', 'tipo_receita': tipo_receita_sem_detalhamento.pk})
    assert not form.is_valid()
    assert 'tipo_receita' in form.errors


def test_form_clean_nome_duplicado_levanta_erro(
        detalhe_tipo_receita_admin, admin_request, detalhe_tipo_receita_parametrizacao):
    form_class = detalhe_tipo_receita_admin.get_form(admin_request)
    form = form_class(data={
        'nome': detalhe_tipo_receita_parametrizacao.nome,
        'tipo_receita': detalhe_tipo_receita_parametrizacao.tipo_receita.pk,
    })
    assert not form.is_valid()
    assert any('detalhe já existe' in e for e in form.non_field_errors())


def test_form_clean_normaliza_nome(detalhe_tipo_receita_admin, admin_request, tipo_receita_com_detalhamento):
    form_class = detalhe_tipo_receita_admin.get_form(admin_request)
    form = form_class(data={'nome': '  Nome   com   espaços  ', 'tipo_receita': tipo_receita_com_detalhamento.pk})
    form.is_valid()
    assert form.cleaned_data.get('nome') == 'Nome com espaços'
