from django.contrib import admin

from .models import TipoTransacao, TipoDocumento, TipoCusteio, EspecificacaoMaterialServico, Despesa, RateioDespesa

admin.site.register(TipoTransacao)
admin.site.register(TipoDocumento)
admin.site.register(TipoCusteio)
admin.site.register(EspecificacaoMaterialServico)
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
    inlines = [RateioDespesaInLine,]
    readonly_fields = ('uuid', 'id')
