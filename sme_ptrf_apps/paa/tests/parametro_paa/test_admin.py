
def test_list_display(parametro_paa_admin):
    assert parametro_paa_admin.list_display == ['__str__', 'mes_elaboracao_paa']


def test_list_display_links(parametro_paa_admin):
    assert parametro_paa_admin.list_display_links == ['__str__']


def test_fieldsets(parametro_paa_admin):
    assert parametro_paa_admin.fieldsets == (
        ('Elaboração', {
            'fields':
                ('mes_elaboracao_paa',)
        }),
        ('Texto PAA (UE)', {
            'fields':
                ('texto_pagina_paa_ue', 'introducao_do_paa_ue_1', 'introducao_do_paa_ue_2', 'conclusao_do_paa_ue_1', 'conclusao_do_paa_ue_2')
        }),
    )
