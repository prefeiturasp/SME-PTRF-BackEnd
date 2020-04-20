from django.contrib import admin

from .models import TipoConta, Acao, Associacao, ContaAssociacao, AcaoAssociacao, Periodo, Unidade, FechamentoPeriodo

admin.site.register(TipoConta)
admin.site.register(Acao)


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    def get_nome_escola(self, obj):
        return obj.nome if obj else ''
    get_nome_escola.short_description = 'Escola'

    list_display = ('nome', 'cnpj', 'get_nome_escola' )
    search_fields = ('uuid', 'nome', 'cnpj', 'unidade__nome')
    list_filter = ('unidade__dre',)
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


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('referencia', 'data_inicio_realizacao_despesas', 'data_fim_realizacao_despesas', 'data_prevista_repasse',
                    'data_inicio_prestacao_contas', 'data_fim_prestacao_contas')
    search_fields = ('uuid', 'referencia')
    readonly_fields = ('uuid', 'id')


@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_unidade', 'codigo_eol', 'sigla', 'dre')
    ordering = ('nome',)
    search_fields = ('nome', 'codigo_eol', 'sigla')
    list_filter = ('tipo_unidade', 'dre')
    list_display_links = ('nome',)


@admin.register(FechamentoPeriodo)
class FechamentoPeriodoAdmin(admin.ModelAdmin):
    def get_nome_acao(self, obj):
        return obj.acao_associacao.acao.nome if obj and obj.acao_associacao else ''
    get_nome_acao.short_description = 'Ação'

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''
    get_nome_conta.short_description = 'Conta'

    list_display = ('periodo', 'get_nome_acao', 'get_nome_conta', 'saldo_anterior', 'total_receitas', 'total_despesas', 'saldo_reprogramado', 'status')
    list_filter = ('status',)
    list_display_links = ('periodo',)
    readonly_fields = ('saldo_reprogramado_capital', 'saldo_reprogramado_custeio')
