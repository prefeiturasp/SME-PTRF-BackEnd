from django.contrib import admin

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
    Observacao,
    Parametros,
    Periodo,
    PrestacaoConta,
    RelacaoBens,
    TipoConta,
    Unidade,
)

admin.site.register(TipoConta)
admin.site.register(Acao)
admin.site.register(DemonstrativoFinanceiro)
admin.site.register(Parametros)
admin.site.register(RelacaoBens)
admin.site.register(MembroAssociacao)
admin.site.register(Observacao)


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    def get_nome_escola(self, obj):
        return obj.unidade.nome if obj else ''

    get_nome_escola.short_description = 'Escola'

    def importa_associacoes(self, request, queryset):
        from .services.carga_associacoes import carrega_associacoes
        carrega_associacoes()
        self.message_user(request, "Associações carregadas.")

    importa_associacoes.short_description = 'Fazer carga de Associações'

    actions = ['importa_associacoes', ]
    list_display = ('nome', 'cnpj', 'get_nome_escola', 'get_usuarios')
    search_fields = ('uuid', 'nome', 'cnpj', 'unidade__nome')
    list_filter = ('unidade__dre', 'periodo_inicial')
    readonly_fields = ('uuid', 'id')

    def get_usuarios(self, obj):
        return ','.join([u.name for u in obj.usuarios.all()]) if obj.usuarios else ''

    get_usuarios.short_description = 'Usuários'

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
    readonly_fields = ('saldo_reprogramado_capital', 'saldo_reprogramado_custeio')
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(PrestacaoConta)
class PrestacaoContaAdmin(admin.ModelAdmin):

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    list_display = ('get_eol_unidade', 'periodo', 'get_nome_conta', 'status')
    list_filter = ('status', 'associacao', 'conta_associacao__tipo_conta')
    list_display_links = ('periodo',)
    readonly_fields = ('uuid',)
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(Ata)
class AtaAdmin(admin.ModelAdmin):

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    def get_referencia_periodo(self, obj):
        return obj.periodo.referencia if obj and obj.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_eol_unidade', 'get_referencia_periodo', 'get_nome_conta', 'data_reuniao', 'tipo_ata', 'tipo_reuniao', 'convocacao',
        'parecer_conselho')
    list_filter = ('parecer_conselho', 'tipo_ata', 'tipo_reuniao', 'convocacao', 'associacao', 'conta_associacao__tipo_conta')
    list_display_links = ('get_eol_unidade',)
    readonly_fields = ('uuid', id)
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ['identificador', 'conteudo', 'tipo_carga']
    actions = ['importa_repasses',]

    def importa_repasses(self, request, queryset):
        from sme_ptrf_apps.core.services.processa_cargas import processa_cargas
        processa_cargas(queryset)
        self.message_user(request, "Repasses Carregados")

    importa_repasses.short_description = "Fazer carga de repasses realizados."
