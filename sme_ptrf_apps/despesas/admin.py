from django.contrib import admin

from .models import TipoTransacao, TipoDocumento, TipoCusteio, EspecificacaoMaterialServico, Despesa, RateioDespesa

admin.site.register(TipoTransacao)
admin.site.register(TipoDocumento)
admin.site.register(TipoCusteio)
admin.site.register(RateioDespesa)


class RateioDespesaInLine(admin.TabularInline):
    model = RateioDespesa
    extra = 1  # Quantidade de linhas que serão exibidas.


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'numero_documento', 'data_documento', 'nome_fornecedor', 'valor_total', 'status')
    ordering = ('-data_documento',)
    search_fields = ('numero_documento', 'nome_fornecedor',)
    list_filter = ('status',)
    inlines = [RateioDespesaInLine, ]
    readonly_fields = ('uuid', 'id')


@admin.register(EspecificacaoMaterialServico)
class EspecificacaoMaterialServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'aplicacao_recurso', 'tipo_custeio')
    ordering = ('descricao',)
    search_fields = ('descricao',)
    list_filter = ('aplicacao_recurso', 'tipo_custeio')
    readonly_fields = ('uuid', 'id')
    actions = ['importa_especificacoes', ]

    def importa_especificacoes(self, request, queryset):
        from .services.carga_especificacoes_material_servico import carrega_especificacoes
        carrega_especificacoes()
        self.message_user(request, "Especificações carregadas.")

    importa_especificacoes.short_description = 'Fazer carga de especificações.'
