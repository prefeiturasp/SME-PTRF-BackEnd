from django.contrib import admin
from .models import (Atribuicao, GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade,
                     ItemVerificacaoRegularidade,
                     VerificacaoRegularidadeAssociacao, TecnicoDre, FaqCategoria, Faq, RelatorioConsolidadoDRE,
                     JustificativaRelatorioConsolidadoDRE, ObsDevolucaoRelatorioConsolidadoDRE,
                     ParametroFiqueDeOlhoRelDre, MotivoAprovacaoRessalva, MotivoReprovacao, Comissao, MembroComissao)

admin.site.register(ParametroFiqueDeOlhoRelDre)
admin.site.register(MotivoAprovacaoRessalva)
admin.site.register(MotivoReprovacao)


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
    list_filter = ('associacao', 'lista_verificacao', 'grupo_verificacao', 'item_verificacao')
    readonly_fields = ('uuid', 'id')


@admin.register(TecnicoDre)
class TecnicoDreAdmin(admin.ModelAdmin):
    list_display = ('rf', 'nome', 'dre', 'telefone', 'email')
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


@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ('codigo_eol_unidade', 'nome_unidade', 'nome_tecnico', 'periodo')

    def nome_tecnico(self, obj):
        return obj.tecnico.nome if obj.tecnico else ''

    def codigo_eol_unidade(self, obj):
        return obj.unidade.codigo_eol if obj.unidade else ''

    def nome_unidade(self, obj):
        return obj.unidade.nome if obj.unidade else ''


@admin.register(RelatorioConsolidadoDRE)
class RelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'status')
    list_filter = ('status', 'dre', 'periodo', 'tipo_conta')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome',)


@admin.register(JustificativaRelatorioConsolidadoDRE)
class JustificativaRelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'texto')
    list_filter = ('dre', 'periodo', 'tipo_conta')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome', 'texto')


@admin.register(ObsDevolucaoRelatorioConsolidadoDRE)
class JObsDevolucaoRelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'tipo_devolucao', 'observacao')
    list_filter = (
        'dre', 'periodo', 'tipo_conta', 'tipo_devolucao', 'tipo_devolucao_a_conta', 'tipo_devolucao_ao_tesouro')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome', 'observacao')


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):
    list_display = ['nome', ]
    search_fields = ['nome', ]
    readonly_fields = ['id', 'uuid', 'criado_em', 'alterado_em']


@admin.register(MembroComissao)
class MembroComissaoAdmin(admin.ModelAdmin):
    list_display = ['rf', 'nome', 'email', 'qtd_comissoes', 'dre']
    search_fields = ['rf', 'nome', 'email', 'dre__nome', 'dre__codigo_eol']
    readonly_fields = ['id', 'uuid', 'criado_em', 'alterado_em']
    list_filter = ('dre', 'comissoes')
