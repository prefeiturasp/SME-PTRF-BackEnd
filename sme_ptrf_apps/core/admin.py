from django.contrib import admin

from .models import TipoConta, Acao, Associacao, ContaAssociacao, AcaoAssociacao

admin.site.register(TipoConta)
admin.site.register(Acao)


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'nome')
    search_fields = ('uuid', 'nome',)
    readonly_fields = ('uuid', 'id')


@admin.register(ContaAssociacao)
class ContaAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'tipo_conta', 'status')
    search_fields = ('uuid',)
    list_filter = ('status',)
    readonly_fields = ('uuid', 'id')


@admin.register(AcaoAssociacao)
class AcaoAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'acao', 'status')
    search_fields = ('uuid',)
    list_filter = ('status',)
    readonly_fields = ('uuid', 'id')
