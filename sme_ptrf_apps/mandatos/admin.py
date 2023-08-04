from django.contrib import admin

from .models import Mandato

@admin.register(Mandato)
class MandatoAdmin(admin.ModelAdmin):
    list_display = ('referencia_mandato', 'data_inicial', 'data_final')
