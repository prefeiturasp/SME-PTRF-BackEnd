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
    Paa,
    PrioridadePaa,
    ObjetivoPaa,
    AtividadeEstatutaria,
    AtaPaa,
    ParticipanteAtaPaa,
    AtividadeEstatutariaPaa
)
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa


@admin.register(PeriodoPaa)
class PeriodoPaaAdmin(admin.ModelAdmin):

    list_display = ('id', 'referencia', 'data_inicial', 'data_final')
    search_fields = ('referencia',)
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
        ('Texto PAA (UE)', {
            'fields':
                ('texto_pagina_paa_ue', 'introducao_do_paa_ue_1', 'introducao_do_paa_ue_2',
                 'conclusao_do_paa_ue_1', 'conclusao_do_paa_ue_2')
        }),
    )


class AtividadeEstatutariaPaaInline(admin.TabularInline):
    model = AtividadeEstatutariaPaa
    extra = 1


@admin.register(Paa)
class PaaAdmin(admin.ModelAdmin):
    list_display = ('periodo_paa', 'associacao', 'status')

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    list_display_links = ['periodo_paa']
    list_filter = ('periodo_paa', 'associacao')
    raw_id_fields = ['periodo_paa', 'associacao']
    inlines = [AtividadeEstatutariaPaaInline]


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
    list_filter = ('acao_associacao__associacao', 'paa')
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


@admin.register(PrioridadePaa)
class PrioridadePaaAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'prioridade',
        'recurso',
        'tipo_aplicacao',
        'programa_pdde',
        'tipo_despesa_custeio',
        'especificacao_material',
        'valor_total',
        'paa',
    )
    list_filter = ('recurso', 'prioridade', 'tipo_aplicacao', 'programa_pdde', 'acao_pdde', 'paa')
    raw_id_fields = ('paa', 'acao_pdde', 'acao_associacao', 'programa_pdde', 'tipo_despesa_custeio',
                     'especificacao_material')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em', 'paa_importado')
    search_fields = ('acao_associacao__acao__nome', 'acao_associacao__associacao__nome', 'programa_pdde__nome',
                     'acao_pdde__nome', 'tipo_despesa_custeio__nome', 'especificacao_material__descricao')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return queryset_prioridades_paa(qs)


@admin.register(ObjetivoPaa)
class ObjetivoPaaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status',)
    list_filter = ('status',)
    raw_id_fields = ('paa', )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em',)
    search_fields = ('nome',)


@admin.register(AtividadeEstatutaria)
class AtividadeEstatutariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'mes', 'tipo')
    list_filter = ('status', 'mes', 'tipo')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em',)
    raw_id_fields = ('paa', )
    search_fields = ('nome',)


@admin.register(AtividadeEstatutariaPaa)
class AtividadeEstatutariaPaaAdmin(admin.ModelAdmin):
    list_display = ('atividade_estatutaria', 'paa', 'data', 'criado_em', 'alterado_em',)
    list_filter = ('atividade_estatutaria__status', 'atividade_estatutaria__mes', 'atividade_estatutaria__tipo')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em',)
    raw_id_fields = ('paa', )
    search_fields = ('nome',)


@admin.register(AtaPaa)
class AtaPaaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return f'{obj.paa.associacao.unidade.codigo_eol} - {obj.paa.associacao.unidade.nome}' if obj and obj.paa and obj.paa.associacao and obj.paa.associacao.unidade else ''  # noqa

    get_eol_unidade.short_description = 'Unidade'

    def get_periodo_paa(self, obj):
        return obj.paa.periodo_paa.referencia if obj and obj.paa and obj.paa.periodo_paa else ''

    get_periodo_paa.short_description = 'Período PAA'

    def get_presidente(self, obj):
        return obj.presidente_da_reuniao.nome if obj and obj.presidente_da_reuniao else ''

    get_presidente.short_description = 'Presidente'

    def get_secretario(self, obj):
        return obj.secretario_da_reuniao.nome if obj and obj.secretario_da_reuniao else ''

    get_secretario.short_description = 'Secretário'

    raw_id_fields = ('paa', 'composicao', 'presidente_da_reuniao', 'secretario_da_reuniao')

    list_display = (
        'get_eol_unidade',
        'get_periodo_paa',
        'tipo_ata',
        'get_presidente',
        'get_secretario',
        'parecer_conselho',
        'previa',
    )

    list_filter = (
        'paa__periodo_paa',
        'tipo_ata',
        'previa',
        'parecer_conselho',
        'paa__associacao__unidade__dre'
    )
    list_display_links = ('get_eol_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('paa__associacao__unidade__codigo_eol', 'paa__associacao__unidade__nome',
                     'paa__associacao__unidade__dre__codigo_eol', 'comentarios')


@admin.register(ParticipanteAtaPaa)
class ParticipanteAtaPaaAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.ata_paa.paa.associacao.unidade.codigo_eol} - {obj.ata_paa.paa.associacao.unidade.nome}' if obj and obj.ata_paa and obj.ata_paa.paa and obj.ata_paa.paa.associacao and obj.ata_paa.paa.associacao.unidade else ''  # noqa

    get_unidade.short_description = 'Unidade'

    def get_periodo_paa(self, obj):
        return f'{obj.ata_paa.paa.periodo_paa.referencia}' if obj and obj.ata_paa and obj.ata_paa.paa and obj.ata_paa.paa.periodo_paa else ''

    get_periodo_paa.short_description = 'Período PAA'

    list_display = ['get_unidade', 'get_periodo_paa', 'ata_paa',
                    'identificacao', 'nome', 'cargo', 'membro', 'professor_gremio']

    search_fields = [
        'nome',
        'identificacao',
        'ata_paa__paa__associacao__unidade__codigo_eol',
        'ata_paa__paa__associacao__unidade__nome',
    ]
    list_filter = [
        'ata_paa__paa__periodo_paa',
        'ata_paa__paa__associacao__unidade__tipo_unidade',
        'ata_paa__paa__associacao__unidade__dre',
        'ata_paa__tipo_ata',
        'cargo',
        'membro',
        'professor_gremio',
        ('criado_em', DateRangeFilter),
        ('alterado_em', DateRangeFilter),
    ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('ata_paa',)
