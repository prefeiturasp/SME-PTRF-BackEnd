from django.contrib import admin

from sme_ptrf_apps.receitas.models import Receita, TipoReceita

admin.site.register(TipoReceita)


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor', 'descricao', 'associacao',)
    ordering = ('-data',)
    search_fields = ('descricao',)
    list_filter = ('data',)
    readonly_fields = ('uuid', 'id')
