from django.contrib import admin
from rangefilter.filter import DateRangeFilter
from sme_ptrf_apps.paa.models import PeriodoPaa


@admin.register(PeriodoPaa)
class PeriodoPaaAdmin(admin.ModelAdmin):

    list_display = ('id', 'referencia', 'data_inicial')
    search_fields = (
        'referencia',
    )
    list_filter = (
        ('data_inicial', DateRangeFilter),
        ('data_final', DateRangeFilter),

    )
