from ...admin_filters import (
    AtaListFilter,
)


def test_ata_search_fields(ata_admin):
    assert ata_admin.search_fields == ('associacao__unidade__codigo_eol', 'associacao__unidade__nome',
                                       'associacao__unidade__dre__codigo_eol', 'comentarios')


def test_ata_list_filter(ata_admin):
    assert ata_admin.list_filter == (
        'periodo',
        'tipo_ata',
        'previa',
        'parecer_conselho',
        'associacao__unidade__dre',
        AtaListFilter,
    )


def test_ata_list_display(ata_admin):
    assert ata_admin.list_display == (
        'get_eol_unidade',
        'get_referencia_periodo',
        'tipo_ata',
        'get_presidente',
        'get_secretario',
        'parecer_conselho',
        'previa',
    )


def test_ata_readonly_fields(ata_admin):
    assert ata_admin.readonly_fields == ('uuid', 'id', 'criado_em', 'alterado_em')


def test_ata_list_display_links(ata_admin):
    assert ata_admin.list_display_links == ('get_eol_unidade',)


def test_ata_raw_id_fields(ata_admin):
    assert ata_admin.raw_id_fields == ('prestacao_conta', 'associacao', 'composicao', 'presidente_da_reuniao',
                                       'secretario_da_reuniao')
