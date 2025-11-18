import pytest
from django.contrib import admin

from sme_ptrf_apps.paa.admin import AtaPaaAdmin, ParticipanteAtaPaaAdmin
from sme_ptrf_apps.paa.models import AtaPaa, ParticipanteAtaPaa

pytestmark = pytest.mark.django_db


def test_ata_paa_admin_registered():
    # pylint: disable=W0212
    assert admin.site._registry[AtaPaa]


def test_ata_paa_admin_list_display(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    expected_list_display = (
        'get_eol_unidade',
        'get_periodo_paa',
        'tipo_ata',
        'get_presidente',
        'get_secretario',
        'parecer_conselho',
        'previa',
    )
    assert model_admin.list_display == expected_list_display


def test_ata_paa_admin_list_display_links(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    assert model_admin.list_display_links == ('get_eol_unidade',)


def test_ata_paa_admin_raw_id_fields(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    expected_raw_id_fields = ('paa', 'composicao', 'presidente_da_reuniao', 'secretario_da_reuniao')
    assert model_admin.raw_id_fields == expected_raw_id_fields


def test_ata_paa_admin_list_filter(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    expected_list_filter = (
        'paa__periodo_paa',
        'tipo_ata',
        'previa',
        'parecer_conselho',
        'paa__associacao__unidade__dre'
    )
    assert model_admin.list_filter == expected_list_filter


def test_ata_paa_admin_search_fields(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    expected_search_fields = (
        'paa__associacao__unidade__codigo_eol',
        'paa__associacao__unidade__nome',
        'paa__associacao__unidade__dre__codigo_eol',
        'comentarios'
    )
    assert model_admin.search_fields == expected_search_fields


def test_ata_paa_admin_readonly_fields(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    expected_readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    assert model_admin.readonly_fields == expected_readonly_fields


def test_ata_paa_admin_get_eol_unidade(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    result = model_admin.get_eol_unidade(ata_paa)
    assert result == f'{ata_paa.paa.associacao.unidade.codigo_eol} - {ata_paa.paa.associacao.unidade.nome}'


def test_ata_paa_admin_get_periodo_paa(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    result = model_admin.get_periodo_paa(ata_paa)
    assert result == ata_paa.paa.periodo_paa.referencia


def test_ata_paa_admin_get_presidente(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    result = model_admin.get_presidente(ata_paa)
    if ata_paa.presidente_da_reuniao:
        assert result == ata_paa.presidente_da_reuniao.nome
    else:
        assert result == ''


def test_ata_paa_admin_get_secretario(ata_paa):
    model_admin = AtaPaaAdmin(AtaPaa, admin.site)
    result = model_admin.get_secretario(ata_paa)
    if ata_paa.secretario_da_reuniao:
        assert result == ata_paa.secretario_da_reuniao.nome
    else:
        assert result == ''


def test_participante_ata_paa_admin_registered():
    # pylint: disable=W0212
    assert admin.site._registry[ParticipanteAtaPaa]


def test_participante_ata_paa_admin_list_display(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    expected_list_display = [
        'get_unidade',
        'get_periodo_paa',
        'ata_paa',
        'identificacao',
        'nome',
        'cargo',
        'membro',
        'professor_gremio'
    ]
    assert model_admin.list_display == expected_list_display


def test_participante_ata_paa_admin_raw_id_fields(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    assert model_admin.raw_id_fields == ('ata_paa',)


def test_participante_ata_paa_admin_list_filter(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    expected_list_filter_fields = [
        'ata_paa__paa__periodo_paa',
        'ata_paa__paa__associacao__unidade__tipo_unidade',
        'ata_paa__paa__associacao__unidade__dre',
        'ata_paa__tipo_ata',
        'cargo',
        'membro',
        'professor_gremio',
    ]
    assert model_admin.list_filter[:7] == expected_list_filter_fields
    assert len(model_admin.list_filter) == 9
    assert isinstance(model_admin.list_filter[7], tuple)
    assert isinstance(model_admin.list_filter[8], tuple)


def test_participante_ata_paa_admin_search_fields(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    expected_search_fields = [
        'nome',
        'identificacao',
        'ata_paa__paa__associacao__unidade__codigo_eol',
        'ata_paa__paa__associacao__unidade__nome',
    ]
    assert model_admin.search_fields == expected_search_fields


def test_participante_ata_paa_admin_readonly_fields(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    expected_readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    assert model_admin.readonly_fields == expected_readonly_fields


def test_participante_ata_paa_admin_get_unidade(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    result = model_admin.get_unidade(presente_ata_paa_membro)
    expected = f'{presente_ata_paa_membro.ata_paa.paa.associacao.unidade.codigo_eol} - {presente_ata_paa_membro.ata_paa.paa.associacao.unidade.nome}'
    assert result == expected


def test_participante_ata_paa_admin_get_periodo_paa(presente_ata_paa_membro):
    model_admin = ParticipanteAtaPaaAdmin(ParticipanteAtaPaa, admin.site)
    result = model_admin.get_periodo_paa(presente_ata_paa_membro)
    expected = f'{presente_ata_paa_membro.ata_paa.paa.periodo_paa.referencia}'
    assert result == expected

