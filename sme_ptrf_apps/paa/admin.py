from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from sme_ptrf_apps.paa.models import (
    ProgramaPdde,
    AcaoPdde,
    ReceitaPrevistaPaa,
    FonteRecursoPaa,
    RecursoProprioPaa,
    PeriodoPaa,
    ParametroPaa,
    ReceitaPrevistaPdde,
    Paa)


@admin.register(PeriodoPaa)
class PeriodoPaaAdmin(admin.ModelAdmin):

    list_display = ('id', 'referencia', 'data_inicial', 'data_final')
    search_fields = (
        'referencia',
    )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    list_filter = (
        ('data_inicial', DateRangeFilter),
        ('data_final', DateRangeFilter),

    )


@admin.register(ParametroPaa)
class ParametroPaaAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'mes_elaboracao_paa',
    ]

    list_display_links = ['__str__']

    fieldsets = (
        ('Elaboração', {
            'fields':
                ('mes_elaboracao_paa',)
        }),
    )


@admin.register(Paa)
class PaaAdmin(admin.ModelAdmin):
    list_display = [
        'periodo_paa',
        'associacao',
    ]

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    list_display_links = ['periodo_paa']
    list_filter = ('periodo_paa', 'associacao')
    raw_id_fields = ['periodo_paa', 'associacao']


@admin.register(ProgramaPdde)
class ProgramaPddeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    list_filter = ('nome',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(AcaoPdde)
class AcaoPddeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'programa')
    search_fields = ('nome', 'programa__nome')
    list_filter = ('programa',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(ReceitaPrevistaPaa)
class ReceitaPrevistaPaaAdmin(admin.ModelAdmin):
    list_display = ('acao_associacao', 'previsao_valor_custeio', 'previsao_valor_capital', 'previsao_valor_livre')
    search_fields = ('acao_associacao__acao__nome', 'acao_associacao__associacao__nome')
    list_filter = ('acao_associacao__associacao',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('acao_associacao', 'paa')


@admin.register(FonteRecursoPaa)
class FonteRecursoPaaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(RecursoProprioPaa)
class RecursoProprioPaaAdmin(admin.ModelAdmin):
    list_display = ('fonte_recurso', 'associacao', 'data_prevista', 'descricao', 'valor',)
    search_fields = ('fonte_recurso__nome', 'associacao__nome',)
    list_filter = ('associacao',)
    raw_id_fields = ('paa', 'associacao', 'fonte_recurso')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(ReceitaPrevistaPdde)
class ReceitaPrevistaPddeAdmin(admin.ModelAdmin):
    list_display = ('paa',
                    'acao_pdde',
                    'previsao_valor_custeio',
                    'previsao_valor_capital',
                    'previsao_valor_livre',
                    'saldo_custeio',
                    'saldo_capital',
                    'saldo_livre'
                    )
    list_filter = ('acao_pdde', 'acao_pdde__programa')
    raw_id_fields = ('paa', 'acao_pdde')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
