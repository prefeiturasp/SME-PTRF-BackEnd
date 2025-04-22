from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from sme_ptrf_apps.core.models import Periodo

from .models import TipoTransacao, TipoDocumento, TipoCusteio, EspecificacaoMaterialServico, Despesa, RateioDespesa, \
    Fornecedor, MotivoPagamentoAntecipado


@admin.register(MotivoPagamentoAntecipado)
class MotivoPagamentoAntecipadoAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'uuid')
    readonly_fields = ('id', 'uuid')


def customTitledFilter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = (
    'nome', 'pode_reter_imposto', 'eh_documento_de_retencao_de_imposto', 'documento_comprobatorio_de_despesa')
    readonly_fields = ('id', 'uuid')


@admin.register(TipoCusteio)
class TipoCusteioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'uuid', 'eh_tributos_e_tarifas')
    readonly_fields = ('id', 'uuid')


@admin.register(RateioDespesa)
class RateioDespesaAdmin(admin.ModelAdmin):
    list_display = (
    "uuid", 'numero_documento', 'associacao', 'acao', 'valor_rateio', 'quantidade_itens_capital', 'status',)
    search_fields = (
        'despesa__numero_documento', 'despesa__nome_fornecedor', 'especificacao_material_servico__descricao',
        'associacao__unidade__codigo_eol', 'associacao__unidade__nome',)
    list_filter = (
        ('conferido', customTitledFilter('Conferido')),
        ('tag', customTitledFilter('Tag')),
        ('associacao__unidade__dre', customTitledFilter('DRE')),
        ('acao_associacao__acao__nome', customTitledFilter('Ação')),
        ('conta_associacao__tipo_conta__nome', customTitledFilter('Tipo Conta')),
        ('aplicacao_recurso', customTitledFilter('Tipo Despesa')),
        ('tipo_custeio', customTitledFilter('Tipo Custeio')),
        ('despesa__tipo_documento', customTitledFilter('Tipo Documento')),
        ('despesa__tipo_transacao', customTitledFilter('Tipo Transacao')),
    )
    raw_id_fields = ('despesa', 'associacao', 'acao_associacao', 'conta_associacao', 'especificacao_material_servico')

    def numero_documento(self, obj):
        return obj.despesa.numero_documento if obj and obj.despesa and obj.despesa.numero_documento else ""

    def associacao(self, obj):
        return obj.associacao.nome if obj.associacao else ''

    def acao(self, obj):
        return obj.acao_associacao.acao.nome if obj.acao_associacao else ''

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


class RateioDespesaInLine(admin.TabularInline):
    model = RateioDespesa
    extra = 1  # Quantidade de linhas que serão exibidas.

    search_fields = (
        'despesa__numero_documento', 'despesa__nome_fornecedor', 'especificacao_material_servico__descricao',
        'associacao__unidade__codigo_eol', 'associacao__unidade__nome',)

    autocomplete_fields = ['associacao', 'despesa', 'conta_associacao', 'acao_associacao']

class PeriodoDaDespesaFilter(admin.SimpleListFilter):
    title = 'Periodo da Despesa'
    parameter_name = 'periodo_da_despesa'

    def lookups(self, request, model_admin):
        periodos = Periodo.objects.all()
        return [(periodo.id, periodo) for periodo in periodos]

    def queryset(self, request, queryset):
        if self.value():
            periodo_id = self.value()
            periodo = Periodo.objects.get(pk=periodo_id)
            return queryset.filter(data_transacao__gte=periodo.data_inicio_realizacao_despesas,
                                    data_transacao__lte=periodo.data_fim_realizacao_despesas)
        return queryset

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_documento', 'numero_documento', 'data_documento', 'nome_fornecedor', 'valor_total', 'status',
        'associacao', 'retem_imposto', 'despesa_anterior_ao_uso_do_sistema', 'despesa_anterior_ao_uso_do_sistema_pc_concluida')
    ordering = ('-data_documento',)
    search_fields = (
        'numero_documento',
        'nome_fornecedor',
        'documento_transacao',
        'associacao__nome',
        'associacao__unidade__codigo_eol'
    )
    list_filter = (
        PeriodoDaDespesaFilter,
        'associacao',
        'associacao__unidade__dre',
        'associacao__unidade__tipo_unidade',
        ('data_documento', DateRangeFilter),
        ('data_transacao', DateRangeFilter),
        'status',
        'nome_fornecedor',
        'tipo_documento',
        'tipo_transacao',
        'eh_despesa_sem_comprovacao_fiscal',
        'eh_despesa_reconhecida_pela_associacao',
        'retem_imposto',
        'despesa_anterior_ao_uso_do_sistema',
        'despesa_anterior_ao_uso_do_sistema_pc_concluida',
    )
    inlines = [RateioDespesaInLine, ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    filter_horizontal = ('despesas_impostos', 'motivos_pagamento_antecipado')

    def associacao(self, obj):
        return obj.associacao.nome if obj.associacao else ''

    raw_id_fields = ['associacao', 'despesas_impostos']


@admin.register(EspecificacaoMaterialServico)
class EspecificacaoMaterialServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'aplicacao_recurso', 'tipo_custeio', 'ativa')
    ordering = ('descricao',)
    search_fields = ('descricao',)
    list_filter = ('aplicacao_recurso', 'tipo_custeio', 'ativa')
    readonly_fields = ('uuid', 'id')
    actions = ['importa_especificacoes', ]
    list_editable = ('ativa',)

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
