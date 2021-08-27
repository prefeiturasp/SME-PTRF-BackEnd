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
    Tag,
    TipoConta,
    Unidade,
    Notificacao,
    CobrancaPrestacaoConta,
    DevolucaoPrestacaoConta,
    AnaliseContaPrestacaoConta,
    TipoDevolucaoAoTesouro,
    DevolucaoAoTesouro,
    ComentarioAnalisePrestacao,
    PrevisaoRepasseSme,
    Censo,
    ParametroFiqueDeOlhoPc,
    ModeloCarga,
    Ambiente,
    ArquivoDownload,
    AnalisePrestacaoConta,
    AnaliseLancamentoPrestacaoConta,
    TipoAcertoLancamento,
    SolicitacaoAcertoLancamento,
)

admin.site.register(Acao)
admin.site.register(ParametroFiqueDeOlhoPc)
admin.site.register(ModeloCarga)


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    def get_nome_escola(self, obj):
        return obj.unidade.nome if obj else ''

    get_nome_escola.short_description = 'Escola'

    list_display = ('nome', 'cnpj', 'get_nome_escola')
    search_fields = ('uuid', 'nome', 'cnpj', 'unidade__nome')
    list_filter = ('unidade__dre', 'periodo_inicial')
    readonly_fields = ('uuid', 'id')
    list_display_links = ('nome', 'cnpj')


@admin.register(ContaAssociacao)
class ContaAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'tipo_conta', 'status')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('status', 'associacao', 'tipo_conta')
    readonly_fields = ('uuid', 'id')


@admin.register(AcaoAssociacao)
class AcaoAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'acao', 'status', 'criado_em')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
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
    list_display = ('nome', 'tipo_unidade', 'codigo_eol', 'sigla', 'dre', 'qtd_alunos')
    ordering = ('nome',)
    search_fields = ('nome', 'codigo_eol', 'sigla')
    list_filter = ('tipo_unidade', 'dre')
    list_display_links = ('nome', 'codigo_eol')
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
    list_display = ['identificador', 'conteudo', 'tipo_carga', 'status', 'ultima_execucao']
    actions = ['processa_carga', ]
    readonly_fields = ['ultima_execucao', 'status', 'log']
    list_filter = ['tipo_carga', 'status']
    search_fields = ('identificador', )

    def processa_carga(self, request, queryset):
        processa_cargas(queryset)
        self.message_user(request, f"Processo Terminado. Verifique o status do processo.")

    processa_carga.short_description = "Realizar Carga dos arquivos."


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome', 'status']
    search_fields = ['nome',]
    list_filter = ['status',]


@admin.register(ProcessoAssociacao)
class ProcessoAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'numero_processo', 'ano')
    search_fields = ('uuid', 'numero_processo')
    list_filter = ('ano', 'associacao',)
    readonly_fields = ('uuid', 'id')


@admin.register(ObservacaoConciliacao)
class ObservacaoConciliacaoAdmin(admin.ModelAdmin):
    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    list_display = ('associacao', 'periodo', 'get_nome_conta', 'data_extrato', 'saldo_extrato', 'texto')
    list_filter = ('associacao', 'conta_associacao__tipo_conta')
    list_display_links = ('periodo',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('texto',)
    autocomplete_fields = ['associacao', 'conta_associacao', 'periodo']


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("uuid", "titulo", "remetente", "categoria", "tipo", "hora")
    readonly_fields = ('uuid', 'id')
    list_filter = ("remetente", "categoria", "tipo")
    search_fields = ("titulo",)


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


@admin.register(AnaliseContaPrestacaoConta)
class AnaliseContaPrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'data_extrato', 'saldo_extrato')
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')


@admin.register(TipoDevolucaoAoTesouro)
class TipoDevolucaoTesouroAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome']
    search_fields = ['nome']


@admin.register(DevolucaoAoTesouro)
class DevolucaoAoTesouroAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'data', 'tipo', 'devolucao_total', 'valor', 'visao_criacao')

    list_filter = (
        'prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta', 'tipo', 'devolucao_total',
        'visao_criacao')

    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'motivo')


@admin.register(ComentarioAnalisePrestacao)
class ComentarioAnalisePrestacaoAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'ordem', 'comentario')
    list_filter = (
        'prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'ordem', 'comentario')


@admin.register(PrevisaoRepasseSme)
class PrevisaoRepasseSmeAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'conta_associacao', 'periodo', 'valor_capital', 'valor_custeio', 'valor_livre')
    list_filter = ('associacao', 'periodo', 'conta_associacao')
    list_display_links = ('associacao',)
    readonly_fields = ('uuid',)
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome')


@admin.register(TipoConta)
class TipoContaAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome']
    search_fields = ['nome']
    list_filter = ['nome', ]
    readonly_fields = ('id', 'uuid',)


@admin.register(Censo)
class CensoAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'unidade', 'quantidade_alunos', 'ano']
    list_filter = ['ano', ]


@admin.register(Parametros)
class ParametrosAdmin(admin.ModelAdmin):
    exclude = ('fique_de_olho', 'fique_de_olho_relatorio_dre')
    list_display = ['permite_saldo_conta_negativo', 'tempo_notificar_nao_demonstrados', ]
    list_display_links = ['permite_saldo_conta_negativo', 'tempo_notificar_nao_demonstrados', ]


@admin.register(DemonstrativoFinanceiro)
class DemonstrativoFinanceiroAdmin(admin.ModelAdmin):

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    def get_nome_associacao(self, obj):
        return obj.conta_associacao.associacao.nome if obj and obj.conta_associacao and obj.conta_associacao.associacao else ''

    get_nome_associacao.short_description = 'Associação'

    def get_periodo(self, obj):
        if obj and obj.prestacao_conta:
            return obj.prestacao_conta.periodo.referencia if obj.prestacao_conta.periodo else ''
        else:
            return obj.periodo_previa.referencia if obj.periodo_previa else ''

    get_periodo.short_description = 'Periodo'

    def get_nome_dre(self, obj):
        return obj.conta_associacao.associacao.unidade.dre.nome if obj and obj.conta_associacao and obj.conta_associacao.associacao and obj.conta_associacao.associacao.unidade and obj.conta_associacao.associacao.unidade.dre else ''

    get_nome_dre.short_description = 'DRE'

    def gera_pdf(self, request, queryset):
        from sme_ptrf_apps.core.models import AcaoAssociacao, ContaAssociacao
        from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
        from sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf

        demonstrativo_financeiro = queryset.first()

        prestacao = demonstrativo_financeiro.prestacao_conta
        periodo = prestacao.periodo
        acoes = prestacao.associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        contas = prestacao.associacao.contas.filter(status=ContaAssociacao.STATUS_ATIVA)

        dados_demonstrativo = gerar_dados_demonstrativo_financeiro("usuarioteste", acoes, periodo, contas[0],
                                                                   prestacao, previa=False)

        gerar_arquivo_demonstrativo_financeiro_pdf(dados_demonstrativo, demonstrativo_financeiro)

    gera_pdf.short_description = "Gerar PDF"

    list_display = (
        'get_nome_associacao',
        'get_periodo',
        'get_nome_conta',
        'get_nome_dre',
        'criado_em',
        'versao',
        'status'
    )

    list_filter = (
        'prestacao_conta__associacao',
        'conta_associacao__tipo_conta',
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__dre',
        'periodo_previa',
        'status',
        'versao'
    )

    list_display_links = ('get_nome_associacao',)

    readonly_fields = ('uuid', 'id',)

    search_fields = (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )

    autocomplete_fields = ['conta_associacao', 'periodo_previa', 'prestacao_conta']

    actions = ['gera_pdf', ]


@admin.register(RelacaoBens)
class RelacaoBensAdmin(admin.ModelAdmin):

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    def get_nome_associacao(self, obj):
        return obj.conta_associacao.associacao.nome if obj and obj.conta_associacao else ''

    get_nome_associacao.short_description = 'Associação'

    def get_periodo(self, obj):
        if obj and obj.prestacao_conta:
            return obj.prestacao_conta.periodo.referencia if obj.prestacao_conta.periodo else ''
        else:
            return obj.periodo_previa.referencia if obj.periodo_previa else ''

    get_periodo.short_description = 'Periodo'

    def get_nome_dre(self, obj):
        return obj.conta_associacao.associacao.unidade.dre.nome if obj and obj.conta_associacao and obj.conta_associacao.associacao and obj.conta_associacao.associacao.unidade and obj.conta_associacao.associacao.unidade.dre else ''

    get_nome_dre.short_description = 'DRE'

    list_display = (
        'get_nome_associacao',
        'get_periodo',
        'get_nome_conta',
        'get_nome_dre',
        'criado_em',
        'versao',
        'status'
    )

    list_filter = (
        'prestacao_conta__associacao',
        'conta_associacao__tipo_conta',
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__dre',
        'periodo_previa',
        'versao',
        'status'
    )

    list_display_links = ('get_nome_associacao',)

    readonly_fields = ('uuid', 'id',)

    search_fields = (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )

    autocomplete_fields = ['conta_associacao', 'periodo_previa', 'prestacao_conta']


@admin.register(MembroAssociacao)
class MembroAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo_associacao', 'associacao')
    search_fields = ('nome', 'codigo_identificacao', 'uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('associacao', 'cargo_associacao', 'representacao')
    readonly_fields = ('uuid', 'id')
    autocomplete_fields = ['associacao', ]


@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('prefixo', 'nome')


@admin.register(ArquivoDownload)
class ArquivoDownloadAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'status', 'alterado_em', 'lido')
    readonly_fields = ('uuid', 'id',)
    list_display_links = ('identificador',)


@admin.register(AnalisePrestacaoConta)
class AnalisePrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = ('get_associacao', 'get_referencia_periodo', 'criado_em', 'status',)
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta', 'status')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', id)
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')


@admin.register(AnaliseLancamentoPrestacaoConta)
class AnaliseLancamentoPrestacaoContaAdmin(admin.ModelAdmin):
    list_display = ['analise_prestacao_conta', 'tipo_lancamento', 'resultado']
    list_filter = ['tipo_lancamento', ]


@admin.register(TipoAcertoLancamento)
class TipoAcertoLancamentoAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome', 'categoria']
    search_fields = ['nome']
    list_filter = ['categoria', ]


@admin.register(SolicitacaoAcertoLancamento)
class SolicitacaoAcertoLancamentoAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'analise_lancamento', 'tipo_acerto']
    search_fields = ['detalhamento']
    list_filter = ['tipo_acerto', ]
