from django.contrib import admin

from sme_ptrf_apps.core.services.processa_cargas import processa_cargas
from .models import (
    Acao,
    AcaoAssociacao,
    Arquivo,
    Associacao,
    Ata,
    ContaAssociacao,
    DemonstrativoFinanceiro,
    FechamentoPeriodo,
    MembroAssociacao,
    ObservacaoConciliacao,
    Parametros,
    Periodo,
    PrestacaoConta,
    ProcessoAssociacao,
    RelacaoBens,
    Remetente,
    Tag,
    TipoConta,
    TipoNotificacao,
    Unidade,
    Categoria,
    Notificacao,
    CobrancaPrestacaoConta,
    DevolucaoPrestacaoConta
)

admin.site.register(TipoConta)
admin.site.register(TipoNotificacao)
admin.site.register(Acao)
admin.site.register(Categoria)
admin.site.register(DemonstrativoFinanceiro)
admin.site.register(Parametros)
admin.site.register(RelacaoBens)
admin.site.register(Remetente)
admin.site.register(MembroAssociacao)


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    def get_nome_escola(self, obj):
        return obj.unidade.nome if obj else ''

    get_nome_escola.short_description = 'Escola'

    list_display = ('nome', 'cnpj', 'get_nome_escola')
    search_fields = ('uuid', 'nome', 'cnpj', 'unidade__nome')
    list_filter = ('unidade__dre', 'periodo_inicial')
    readonly_fields = ('uuid', 'id')


@admin.register(ContaAssociacao)
class ContaAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'tipo_conta', 'status')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol')
    list_filter = ('status', 'associacao', 'tipo_conta')
    readonly_fields = ('uuid', 'id')


@admin.register(AcaoAssociacao)
class AcaoAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'acao', 'status', 'criado_em')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol')
    list_filter = ('status', 'associacao', 'acao')
    readonly_fields = ('uuid', 'id')


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = (
        'referencia', 'data_inicio_realizacao_despesas', 'data_fim_realizacao_despesas', 'data_prevista_repasse',
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
    readonly_fields = ('uuid',)

    fieldsets = (
        ('Dados da Unidade', {
            'fields': (
                'nome',
                'tipo_unidade',
                'codigo_eol',
                'dre',
                'sigla',
                'cep',
                'tipo_logradouro',
                'logradouro',
                'bairro',
                'numero',
                'complemento',
                'telefone',
                'email',
                'qtd_alunos',
                'diretor_nome',
                'uuid'
            )
        }),

        ('Dados da Diretoria da Unidade', {
            'fields': (
                'dre_cnpj',
                'dre_diretor_regional_rf',
                'dre_diretor_regional_nome',
                'dre_designacao_portaria',
                'dre_designacao_ano'
            )
        }),
    )


@admin.register(FechamentoPeriodo)
class FechamentoPeriodoAdmin(admin.ModelAdmin):
    def get_nome_acao(self, obj):
        return obj.acao_associacao.acao.nome if obj and obj.acao_associacao else ''

    get_nome_acao.short_description = 'Ação'

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    list_display = ('get_eol_unidade', 'periodo', 'get_nome_acao', 'get_nome_conta', 'saldo_anterior', 'total_receitas',
                    'total_despesas', 'saldo_reprogramado', 'status')
    list_filter = ('status', 'associacao', 'acao_associacao__acao', 'conta_associacao__tipo_conta')
    list_display_links = ('periodo',)
    readonly_fields = ('saldo_reprogramado_capital', 'saldo_reprogramado_custeio', 'saldo_reprogramado_livre')
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(PrestacaoConta)
class PrestacaoContaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    list_display = ('get_eol_unidade', 'periodo', 'status')
    list_filter = ('status', 'associacao', 'periodo')
    list_display_links = ('periodo',)
    readonly_fields = ('uuid',)
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(Ata)
class AtaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    def get_referencia_periodo(self, obj):
        return obj.periodo.referencia if obj and obj.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_eol_unidade', 'get_referencia_periodo', 'data_reuniao', 'tipo_ata', 'tipo_reuniao',
        'convocacao',
        'parecer_conselho')
    list_filter = (
        'parecer_conselho', 'tipo_ata', 'tipo_reuniao', 'convocacao', 'associacao')
    list_display_links = ('get_eol_unidade',)
    readonly_fields = ('uuid', id)
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ['identificador', 'conteudo', 'tipo_carga']
    actions = ['processa_carga', ]

    def processa_carga(self, request, queryset):
        processa_cargas(queryset)
        self.message_user(request, "Carga Realizada com sucesso.")

    processa_carga.short_description = "Realizar Carga dos arquivos."


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome', 'status']
    search_fields = ['status']
    list_filter = ['nome', 'status']


@admin.register(ProcessoAssociacao)
class ProcessoAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'numero_processo', 'ano')
    search_fields = ('uuid', 'numero_processo')
    list_filter = ('ano', 'associacao',)
    readonly_fields = ('uuid', 'id')


@admin.register(ObservacaoConciliacao)
class ObservacaoConciliacaoAdmin(admin.ModelAdmin):
    def get_nome_acao(self, obj):
        return obj.acao_associacao.acao.nome if obj and obj.acao_associacao else ''

    get_nome_acao.short_description = 'Ação'

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    list_display = ('associacao', 'periodo', 'get_nome_acao', 'get_nome_conta', 'texto')
    list_filter = ('associacao', 'acao_associacao__acao', 'conta_associacao__tipo_conta')
    list_display_links = ('periodo',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('texto',)


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("uuid", "titulo", "remetente", "categoria", "tipo", "hora")
    readonly_fields = ('uuid', 'id')
    list_filter = ("remetente", "categoria", "tipo")


@admin.register(CobrancaPrestacaoConta)
class CobrancaPrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'data', 'tipo')
    list_filter = ('tipo', 'prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')


@admin.register(DevolucaoPrestacaoConta)
class DevolucaoPrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'data', 'data_limite_ue')
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')
