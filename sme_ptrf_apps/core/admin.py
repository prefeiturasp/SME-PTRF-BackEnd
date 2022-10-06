import logging

from django.contrib import admin
from rangefilter.filter import DateRangeFilter
from sme_ptrf_apps.core.services.processa_cargas import processa_cargas
from sme_ptrf_apps.core.services import associacao_pode_implantar_saldo
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
    TipoDocumentoPrestacaoConta,
    TipoAcertoDocumento,
    AnaliseDocumentoPrestacaoConta,
    SolicitacaoAcertoDocumento,
    PresenteAta,
    ValoresReprogramados,
    SolicitacaoDevolucaoAoTesouro
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

    actions = ['define_status_nao_finalizado_valores_reprogramados', 'migrar_valores_reprogramados']

    def define_status_nao_finalizado_valores_reprogramados(self, request, queryset):
        for associacao in queryset.all():
            implantacao = associacao_pode_implantar_saldo(associacao=associacao)

            if implantacao["permite_implantacao"]:
                associacao.status_valores_reprogramados = Associacao.STATUS_VALORES_REPROGRAMADOS_NAO_FINALIZADO
                associacao.save()

        self.message_user(request, f"Status definido com sucesso!")

    def migrar_valores_reprogramados(self, request, queryset):
        for associacao in queryset.all():
            if associacao.status_valores_reprogramados == Associacao.STATUS_VALORES_REPROGRAMADOS_VALORES_CORRETOS:
                # caso ja exista valores reprogramados para essa associação, nada deve ser feito
                if associacao.valores_reprogramados_associacao.all():
                    continue

                if not associacao.periodo_inicial:
                    continue

                for conta_associacao in associacao.contas.all():
                    for acao_associacao in associacao.acoes.exclude(acao__e_recursos_proprios=True):
                        fechamento_implantacao = associacao.fechamentos_associacao.filter(
                            conta_associacao=conta_associacao).filter(
                            acao_associacao=acao_associacao).filter(status="IMPLANTACAO").first()

                        if acao_associacao.acao.aceita_custeio:
                            ValoresReprogramados.criar_valor_reprogramado_custeio(
                                associacao,
                                conta_associacao,
                                acao_associacao,
                                fechamento_implantacao
                            )

                        if acao_associacao.acao.aceita_capital:
                            ValoresReprogramados.criar_valor_reprogramado_capital(
                                associacao,
                                conta_associacao,
                                acao_associacao,
                                fechamento_implantacao
                            )

                        if acao_associacao.acao.aceita_livre:
                            ValoresReprogramados.criar_valor_reprogramado_livre(
                                associacao,
                                conta_associacao,
                                acao_associacao,
                                fechamento_implantacao
                            )

        self.message_user(request, f"Valores migrados com sucesso!")


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
    readonly_fields = (
    'saldo_reprogramado_capital', 'saldo_reprogramado_custeio', 'saldo_reprogramado_livre', 'uuid', 'id')
    search_fields = ('associacao__unidade__codigo_eol',)


@admin.register(PrestacaoConta)
class PrestacaoContaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    def get_nome_unidade(self, obj):
        return obj.associacao.unidade.nome if obj and obj.associacao and obj.associacao.unidade else ''

    get_nome_unidade.short_description = 'Unidade Educacional'

    def get_relatorio_referencia(self, obj):
        return obj.consolidado_dre.referencia if obj.consolidado_dre else ""

    get_relatorio_referencia.short_description = 'Publicação'

    def get_periodo_referencia(self, obj):
        return obj.periodo.referencia if obj.periodo else ""

    get_periodo_referencia.short_description = 'Período'

    list_display = (
        'get_eol_unidade',
        'get_nome_unidade',
        'get_periodo_referencia',
        'status',
        'publicada',
        'get_relatorio_referencia'
    )
    list_filter = (
        'status',
        'associacao__unidade__dre',
        'associacao',
        'periodo',
        'publicada',
        'consolidado_dre__sequencia_de_publicacao',
        'consolidado_dre'
    )
    list_display_links = ('get_nome_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__nome')

    actions = ['vincular_consolidado_dre', 'remover_duplicacao_fechamentos']

    def vincular_consolidado_dre(self, request, queryset):
        from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

        for prestacao_conta in queryset.all():
            VincularConsolidadoService.vincular_artefato(prestacao_conta)

        self.message_user(request, f"PCs vinculadas com sucesso!")

    def remover_duplicacao_fechamentos(self, request, queryset):
        for prestacao_conta in queryset.all():
            associacao = prestacao_conta.associacao

            for conta in associacao.contas.all():
                fechamento_por_conta = prestacao_conta.fechamentos_da_prestacao.filter(conta_associacao=conta)

                for acao in associacao.acoes.all():
                    fechamento_por_conta_e_acao = fechamento_por_conta.filter(acao_associacao=acao).order_by('id')

                    if len(fechamento_por_conta_e_acao) > 1:
                        fechamento_mais_recente = fechamento_por_conta_e_acao.last()
                        fechamento_mais_recente.delete()

        self.message_user(request, f"Fechamentos duplicados apagados com sucesso!")


@admin.register(Ata)
class AtaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return f'{obj.associacao.unidade.codigo_eol} - {obj.associacao.unidade.nome}' if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        return obj.periodo.referencia if obj and obj.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_eol_unidade',
        'get_referencia_periodo',
        'tipo_ata',
        'parecer_conselho',
        'previa',
        'arquivo_pdf',
    )

    list_filter = (
        'periodo',
        'tipo_ata',
        'previa',
        'parecer_conselho',
    )
    list_display_links = ('get_eol_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__unidade__nome')


@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ['identificador', 'conteudo', 'tipo_carga', 'status', 'ultima_execucao']
    actions = ['processa_carga', ]
    readonly_fields = ['ultima_execucao', 'status', 'log', 'uuid', 'id']
    list_filter = ['tipo_carga', 'status']
    search_fields = ('identificador',)

    def processa_carga(self, request, queryset):
        processa_cargas(queryset)
        self.message_user(request, f"Processo Terminado. Verifique o status do processo.")

    processa_carga.short_description = "Realizar Carga dos arquivos."


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nome', 'status']
    search_fields = ['nome', ]
    list_filter = ['status', ]
    readonly_fields = ('uuid', id)


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
    def get_codigo_eol(self, obj):
        if obj and obj.unidade:
            return obj.unidade.codigo_eol
        else:
            return ''

    get_codigo_eol.short_description = 'EOL'

    def get_referencia_pc(self, obj):
        if obj and obj.prestacao_conta and obj.prestacao_conta.periodo:
            return obj.prestacao_conta.periodo.referencia
        else:
            return ''

    get_referencia_pc.short_description = 'PC'

    list_display = ("titulo", "categoria", "usuario", "get_codigo_eol", "get_referencia_pc", "criado_em", "lido")
    readonly_fields = ('uuid', 'id', 'criado_em', "hora")
    list_filter = (
        ('criado_em', DateRangeFilter),
        "remetente", "categoria",
        "tipo", "usuario",
        "unidade", "prestacao_conta",
        "lido",
    )
    search_fields = ("titulo", "unidade__nome", "usuario__name", "unidade__codigo_eol", "descricao",
                     "prestacao_conta__periodo__referencia")
    autocomplete_fields = ['unidade', 'prestacao_conta']


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
    readonly_fields = ('uuid', 'id')
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

    def get_id_analise_prestacao_contas(self, obj):
        return obj.analise_prestacao_conta.id if obj and obj.analise_prestacao_conta and obj.analise_prestacao_conta.id else ''

    get_id_analise_prestacao_contas.short_description = 'Análise de Prestação de contas'

    list_display = (
        'get_associacao', 'get_referencia_periodo', 'data_extrato', 'saldo_extrato', 'get_id_analise_prestacao_contas')
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta',
                   'analise_prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')

    actions = ['vincula_analise_prestacao_contas', ]

    def vincula_analise_prestacao_contas(self, request, queryset):
        for analise_conta in queryset.all():
            # verifica se ja possui analise de pc
            if not analise_conta.analise_prestacao_conta:
                # verifica se existe alguma analise de pc para essa pc
                if analise_conta.prestacao_conta.analises_da_prestacao.all():
                    ultima_analise = analise_conta.prestacao_conta.analises_da_prestacao.latest('id')
                    if ultima_analise:
                        analise_conta.analise_prestacao_conta = ultima_analise
                        analise_conta.save()

        self.message_user(request, f"Vinculação Concluída.")

    vincula_analise_prestacao_contas.short_description = "Víncular a ultima análise de prestação de contas"


@admin.register(TipoDevolucaoAoTesouro)
class TipoDevolucaoTesouroAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'nome']
    search_fields = ['nome']
    readonly_fields = ('uuid', id)


@admin.register(DevolucaoAoTesouro)
class DevolucaoAoTesouroAdmin(admin.ModelAdmin):

    def get_unidade(self, obj):
        return f'{obj.prestacao_conta.associacao.unidade.codigo_eol} - {obj.prestacao_conta.associacao.unidade.nome}' if obj and obj.prestacao_conta and obj.prestacao_conta.associacao and obj.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_unidade', 'get_referencia_periodo', 'despesa', 'data', 'tipo', 'devolucao_total', 'valor', 'visao_criacao')

    list_filter = (
        'prestacao_conta__periodo', 'prestacao_conta', 'tipo', 'devolucao_total',
        'visao_criacao', 'data')

    list_display_links = ('get_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
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
        'get_associacao', 'get_referencia_periodo', 'ordem', 'comentario', 'notificado_em')
    list_filter = (
        'prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'ordem', 'comentario')


@admin.register(PrevisaoRepasseSme)
class PrevisaoRepasseSmeAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'conta_associacao', 'periodo', 'valor_capital', 'valor_custeio', 'valor_livre')
    list_filter = ('associacao', 'periodo', 'conta_associacao')
    list_display_links = ('associacao',)
    readonly_fields = ('uuid', 'id')
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
        from sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service import \
            gerar_arquivo_demonstrativo_financeiro_pdf

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
    search_fields = (
    'nome', 'codigo_identificacao', 'uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome',
    'associacao__nome')
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
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta', 'status',
                   'status_versao', 'versao', 'status_versao_apresentacao_apos_acertos',
                   'versao_pdf_apresentacao_apos_acertos',)
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')


@admin.register(AnaliseLancamentoPrestacaoConta)
class AnaliseLancamentoPrestacaoContaAdmin(admin.ModelAdmin):
    list_display = ['analise_prestacao_conta', 'tipo_lancamento', 'resultado', 'status_realizacao',
                    'devolucao_tesouro_atualizada']
    list_filter = (
    'analise_prestacao_conta__prestacao_conta__associacao__unidade',
    'analise_prestacao_conta__prestacao_conta__periodo',
    'tipo_lancamento',
    'devolucao_tesouro_atualizada',
    )
    readonly_fields = ('uuid', 'id',)


@admin.register(TipoAcertoLancamento)
class TipoAcertoLancamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'ativo']
    search_fields = ['nome', 'categoria']
    list_filter = ['nome', 'categoria', 'ativo']
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(SolicitacaoAcertoLancamento)
class SolicitacaoAcertoLancamentoAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol} - {obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}' if obj and obj.analise_lancamento and obj.analise_lancamento.analise_prestacao_conta and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_despesa(self, obj):
        return obj.analise_lancamento.despesa if obj and obj.analise_lancamento else ''

    get_despesa.short_description = 'Despesa'

    list_display = ['get_unidade', 'analise_lancamento', 'tipo_acerto', 'devolucao_ao_tesouro', 'get_despesa', 'copiado']
    search_fields = [
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'detalhamento',
    ]
    list_filter = [
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo__referencia',
        'tipo_acerto',
        'devolucao_ao_tesouro',
        'copiado'
    ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    actions = ['buscar_e_vincular_devolucao_ao_tesouro']

    def buscar_e_vincular_devolucao_ao_tesouro(self, request, queryset):
        for solicitacao in queryset.all():
            if solicitacao.tipo_acerto.categoria != 'DEVOLUCAO' or solicitacao.devolucao_ao_tesouro:
                continue

            prestacao_conta = solicitacao.analise_lancamento.analise_prestacao_conta.prestacao_conta
            despesa = solicitacao.analise_lancamento.despesa
            devolucao = DevolucaoAoTesouro.objects.filter(prestacao_conta=prestacao_conta, despesa=despesa).first()

            if devolucao:
                solicitacao.devolucao_ao_tesouro = devolucao
                solicitacao.detalhamento = solicitacao.detalhamento + "(**vinculada a dvt)"
                solicitacao.save()
                logging.info(
                    f'Vinculado solicitação {solicitacao.id}-{solicitacao} à devolução {devolucao.id}-{devolucao}')

        self.message_user(request, f"Processo realizado com sucesso!")


@admin.register(TipoDocumentoPrestacaoConta)
class TipoDocumentoPrestacaoContaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    readonly_fields = ('uuid', 'id',)


@admin.register(TipoAcertoDocumento)
class TipoAcertoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'ativo']
    search_fields = ['nome']
    list_filter = ['tipos_documento_prestacao', 'categoria', 'ativo']
    readonly_fields = ('uuid', 'id',)


@admin.register(AnaliseDocumentoPrestacaoConta)
class AnaliseDocumentoPrestacaoContaAdmin(admin.ModelAdmin):
    list_display = ['analise_prestacao_conta', 'tipo_documento_prestacao_conta', 'resultado', 'status_realizacao']
    list_filter = [
        'analise_prestacao_conta__prestacao_conta__associacao__unidade',
        'analise_prestacao_conta__prestacao_conta__periodo',
        'tipo_documento_prestacao_conta',
    ]
    readonly_fields = ('uuid', 'id',)


@admin.register(SolicitacaoAcertoDocumento)
class SolicitacaoAcertoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'analise_documento', 'tipo_acerto', 'copiado',]
    search_fields = ['uuid']
    list_filter = ['tipo_acerto', 'copiado', ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em',)


@admin.register(PresenteAta)
class PresenteAtaAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'ata', 'identificacao', 'nome', 'cargo', 'membro']


@admin.register(ValoresReprogramados)
class ValoresReprogramadosAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'conta_associacao', 'acao_associacao', 'aplicacao_recurso', 'valor_ue', 'valor_dre')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('associacao', 'associacao__status_valores_reprogramados', 'associacao__periodo_inicial',
                   'associacao__unidade__dre', 'conta_associacao__tipo_conta',
                   'acao_associacao__acao', 'aplicacao_recurso')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(SolicitacaoDevolucaoAoTesouro)
class SolicitacaoDevolucaoPrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome

    get_associacao.short_description = 'Associação'

    # def get_referencia_periodo(self, obj):
    #     return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''
    #
    # get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_associacao', 'valor',)
    # list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao', 'prestacao_conta')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id')
    # search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
    #                  'prestacao_conta__associacao__nome')

