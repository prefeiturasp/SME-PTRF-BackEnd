from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from .models import TipoTransacao, TipoDocumento, TipoCusteio, EspecificacaoMaterialServico, Despesa, RateioDespesa, \
    Fornecedor

admin.site.register(TipoDocumento)


def customTitledFilter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.register(TipoCusteio)
class TipoCusteioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'uuid')
    readonly_fields = ('id', 'uuid')


@admin.register(RateioDespesa)
class RateioDespesaAdmin(admin.ModelAdmin):
    list_display = ('numero_documento', 'associacao', 'acao', 'valor_rateio', 'quantidade_itens_capital', 'status')
    search_fields = (
        'despesa__numero_documento', 'despesa__nome_fornecedor', 'especificacao_material_servico__descricao')
    list_filter = (
        ('despesa__data_documento', DateRangeFilter),
        ('associacao__nome', customTitledFilter('Associação')),
        ('associacao__unidade__dre', customTitledFilter('DRE')),
        ('acao_associacao__acao__nome', customTitledFilter('Ação')),
        ('conta_associacao__tipo_conta__nome', customTitledFilter('Tipo Conta')),
        ('aplicacao_recurso', customTitledFilter('Tipo Despesa')),
        ('despesa__numero_documento', customTitledFilter('Número documento')),
        ('tipo_custeio', customTitledFilter('Tipo Custeio')),
        ('despesa__tipo_documento', customTitledFilter('Tipo Documento')),
        ('despesa__tipo_transacao', customTitledFilter('Tipo Transacao')),
        ('despesa__nome_fornecedor', customTitledFilter('Nome Fornecedor')),
        ('especificacao_material_servico__descricao', customTitledFilter('Especificação Material/Serviço')),)

    def numero_documento(self, obj):
        return obj.despesa.numero_documento

    def associacao(self, obj):
        return obj.associacao.nome if obj.associacao else ''

    def acao(self, obj):
        return obj.acao_associacao.acao.nome if obj.acao_associacao else ''


class RateioDespesaInLine(admin.TabularInline):
    model = RateioDespesa
    extra = 1  # Quantidade de linhas que serão exibidas.


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_documento', 'numero_documento', 'data_documento', 'nome_fornecedor', 'valor_total', 'status', 'associacao')
    ordering = ('-data_documento',)
    search_fields = ('numero_documento', 'nome_fornecedor', 'documento_transacao', 'associacao__nome', 'associacao__unidade__codigo_eol')
    list_filter = ('status', 'associacao')
    inlines = [RateioDespesaInLine, ]
    readonly_fields = ('uuid', 'id')

    def associacao(self, obj):
        return obj.associacao.nome if obj.associacao else ''


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


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf_cnpj',)
    ordering = ('nome',)
    search_fields = ('nome', 'cpf_cnpj',)
    readonly_fields = ('uuid', 'id')


@admin.register(TipoTransacao)
class TipoTransacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tem_documento',)
    ordering = ('nome',)
    search_fields = ('nome',)
    readonly_fields = ('uuid', 'id')
