from django.contrib import admin

from .models import (GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade, ItemVerificacaoRegularidade,
                     VerificacaoRegularidadeAssociacao, TecnicoDre, FaqCategoria, Faq)


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

@admin.register(TecnicoDre)
class TecnicoDreAdmin(admin.ModelAdmin):
    list_display = ('rf', 'nome', 'dre')
    search_fields = ('uuid', 'nome', 'rf')
    list_filter = ('dre',)
    readonly_fields = ('uuid', 'id')


@admin.register(FaqCategoria)
class ListaFaqCategorias(admin.ModelAdmin):
    list_display = ('id', 'nome',)
    list_display_links = ('id', 'nome')
    fields = ['nome', 'uuid']
    readonly_fields = ('uuid', 'id')


@admin.register(Faq)
class ListaFaq(admin.ModelAdmin):
    list_display = ('id', 'pergunta', 'resposta', 'categoria',)
    list_display_links = ('id', 'pergunta')
    list_filter = ('categoria',)
    fields = ['pergunta', 'resposta', 'categoria', 'uuid']
    readonly_fields = ('uuid', 'id')
