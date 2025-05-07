from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from sme_ptrf_apps.paa.models import PeriodoPaa, ParametroPaa, Paa


@admin.register(PeriodoPaa)
class PeriodoPaaAdmin(admin.ModelAdmin):

    list_display = ('id', 'referencia', 'data_inicial', 'data_final')
    search_fields = (
        'referencia',
    )
    list_filter = (
        ('data_inicial', DateRangeFilter),
        ('data_final', DateRangeFilter),

    )


@admin.register(ParametroPaa)
class ParametroPaaAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'mes_elaboracao_paa',
    ]

    list_display_links = ['__str__']

    fieldsets = (
        ('Elaboração', {
            'fields':
                ('mes_elaboracao_paa',)
        }),
    )


@admin.register(Paa)
class PaaAdmin(admin.ModelAdmin):
    list_display = [
        'periodo_paa',
        'associacao',
    ]

    list_display_links = ['periodo_paa']
    raw_id_fields = ['periodo_paa', 'associacao']
