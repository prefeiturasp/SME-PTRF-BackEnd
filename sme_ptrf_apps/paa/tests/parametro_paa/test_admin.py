
def test_list_display(parametro_paa_admin):
    assert parametro_paa_admin.list_display == ['__str__', 'mes_elaboracao_paa']


def test_list_display_links(parametro_paa_admin):
    assert parametro_paa_admin.list_display_links == ['__str__']


def fieldsets(parametro_paa_admin):
    assert parametro_paa_admin.fieldsets == (
        ('Elaboração', {
            'fields':
                ('mes_elaboracao_paa',)
        }),
    )
