from django.contrib import admin

from .models import (GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade, ItemVerificacaoRegularidade,
                     VerificacaoRegularidadeAssociacao)


class ListasVerificacaoInline(admin.TabularInline):
    extra = 1
    model = ListaVerificacaoRegularidade


class ItensVerificacaoInline(admin.TabularInline):
    extra = 1
    model = ItemVerificacaoRegularidade


@admin.register(GrupoVerificacaoRegularidade)
class GrupoVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', ]
    search_fields = ['titulo', ]
    readonly_fields = ['id', 'uuid']
    inlines = [
        ListasVerificacaoInline
    ]


@admin.register(ListaVerificacaoRegularidade)
class ListaVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'grupo']
    search_fields = ['titulo', ]
    readonly_fields = ['id', 'uuid']
    inlines = [
        ItensVerificacaoInline
    ]
    list_filter = ('grupo',)


@admin.register(ItemVerificacaoRegularidade)
class ItemVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'lista')
    search_fields = ('uuid', 'descricao')
    list_filter = ('lista', 'lista__grupo')
    readonly_fields = ('uuid', 'id')

@admin.register(VerificacaoRegularidadeAssociacao)
class VerificacaoRegularidadeAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('item_verificacao', 'regular', 'lista_verificacao', 'associacao')
    search_fields = ('uuid', 'item_verificacao__descricao')
    list_filter = ('associacao','lista_verificacao', 'grupo_verificacao', 'item_verificacao')
    readonly_fields = ('uuid', 'id')
