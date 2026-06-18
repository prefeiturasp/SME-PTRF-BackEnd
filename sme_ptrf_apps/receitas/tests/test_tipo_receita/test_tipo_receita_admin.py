import datetime

import pytest
from django.forms import modelform_factory
from model_bakery import baker

from sme_ptrf_apps.receitas.admin import RecursoFilter, TipoReceitaForm
from sme_ptrf_apps.receitas.models import TipoReceita


# TipoReceitaAdmin — atributos de configuração

def test_tipo_receita_admin_list_display(tipo_receita_admin):
    assert tipo_receita_admin.list_display == (
        'nome', 'recurso', 'e_repasse', 'e_rendimento', 'aceita_capital',
        'aceita_custeio', 'aceita_livre', 'mensagem_usuario', 'possui_detalhamento'
    )


def test_tipo_receita_admin_readonly_fields(tipo_receita_admin):
    assert tipo_receita_admin.readonly_fields == ('uuid',)


def test_tipo_receita_admin_autocomplete_fields(tipo_receita_admin):
    assert tipo_receita_admin.autocomplete_fields == ('unidades',)


def test_tipo_receita_admin_list_filter_usa_recurso_filter(tipo_receita_admin):
    assert RecursoFilter in tipo_receita_admin.list_filter


# TipoReceitaForm.clean_unidades()

@pytest.fixture
def bound_tipo_receita_form():
    return modelform_factory(TipoReceita, form=TipoReceitaForm, fields=['nome', 'recurso', 'unidades'])


def test_clean_unidades_sem_selecao_valida(bound_tipo_receita_form, tipo_receita_factory, recurso_legado):
    tipo_receita = tipo_receita_factory.create(nome='Tipo Vazio')
    form = bound_tipo_receita_form(
        data={'nome': tipo_receita.nome, 'recurso': recurso_legado.pk, 'unidades': []},
        instance=tipo_receita,
    )
    assert form.is_valid(), form.errors


def test_clean_unidades_sem_receita_valida(bound_tipo_receita_form, tipo_receita_factory, recurso_legado, unidade):
    tipo_receita = tipo_receita_factory.create(nome='Tipo Sem Receita')
    form = bound_tipo_receita_form(
        data={'nome': tipo_receita.nome, 'recurso': recurso_legado.pk, 'unidades': [unidade.pk]},
        instance=tipo_receita,
    )
    assert form.is_valid(), form.errors


def test_clean_unidades_faltante_levanta_erro(
    bound_tipo_receita_form,
    tipo_receita_factory,
    recurso_legado,
    associacao,
    conta_associacao,
    acao_associacao,
    unidade,
    outra_unidade,
):
    tipo_receita = tipo_receita_factory.create(nome='Tipo Com Receita')
    baker.make(
        'Receita',
        tipo_receita=tipo_receita,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        data=datetime.date(2020, 1, 1),
        valor=100,
    )

    # Seleciona outra_unidade mas não unidade (que tem receita via associacao)
    form = bound_tipo_receita_form(
        data={'nome': tipo_receita.nome, 'recurso': recurso_legado.pk, 'unidades': [outra_unidade.pk]},
        instance=tipo_receita,
    )
    assert not form.is_valid()
    assert 'unidades' in form.errors
