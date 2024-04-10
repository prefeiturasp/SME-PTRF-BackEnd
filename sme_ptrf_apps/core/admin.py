import logging
from django.contrib import admin, messages
from django.forms import ModelForm, ValidationError
from rangefilter.filter import DateRangeFilter
from sme_ptrf_apps.core.services.processa_cargas import processa_cargas
from sme_ptrf_apps.core.services import associacao_pode_implantar_saldo
from sme_ptrf_apps.core.tasks.regerar_demonstrativos_financeiros import regerar_demonstrativo_financeiro_async
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
    RelatorioRelacaoBens,
    ItemRelatorioRelacaoDeBens,
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
    Participante,
    ValoresReprogramados,
    SolicitacaoDevolucaoAoTesouro,
    TransferenciaEol,
    FalhaGeracaoPc,
    SolicitacaoEncerramentoContaAssociacao,
    MotivoRejeicaoEncerramentoContaAssociacao,
    TaskCelery,
    DadosDemonstrativoFinanceiro,
    ItemResumoPorAcao,
    ItemCredito,
    ItemDespesa,
    PrestacaoContaReprovadaNaoApresentacao
)

from django.db.models import Count
from django.utils.safestring import mark_safe

admin.site.register(ParametroFiqueDeOlhoPc)
admin.site.register(ModeloCarga)
admin.site.register(MotivoRejeicaoEncerramentoContaAssociacao)


@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'id')


@admin.register(SolicitacaoEncerramentoContaAssociacao)
class SolicitacaoEncerramentoContaAssociacaoAdmin(admin.ModelAdmin):
    def get_codigo_eol(self, obj):
        return obj.conta_associacao.associacao.unidade.codigo_eol if obj and obj.conta_associacao and obj.conta_associacao.associacao and obj.conta_associacao.associacao.unidade else ''

    get_codigo_eol.short_description = 'EOL'

    raw_id_fields = ('conta_associacao',)
    list_filter = (
        ('data_de_encerramento_na_agencia', DateRangeFilter),
        ('conta_associacao__associacao__unidade__dre'),
    )
    list_display = ('__str__', 'get_codigo_eol')
    search_fields = ('uuid', 'conta_associacao__uuid', 'conta_associacao__associacao__unidade__codigo_eol',
                     'conta_associacao__associacao__unidade__nome', 'conta_associacao__associacao__nome',
                     'conta_associacao__associacao__unidade__dre__codigo_eol')


@admin.register(Associacao)
class AssociacaoAdmin(admin.ModelAdmin):
    def get_nome_escola(self, obj):
        return obj.unidade.nome if obj else ''

    get_nome_escola.short_description = 'Escola'

    def get_periodo_inicial_referencia(self, obj):
        return obj.periodo_inicial.referencia if obj and obj.periodo_inicial else ''

    get_periodo_inicial_referencia.short_description = 'Período Inicial'

    list_display = ('nome', 'cnpj', 'get_nome_escola', 'get_periodo_inicial_referencia',
                    'data_de_encerramento', 'migrada_para_historico_de_membros')
    search_fields = ('uuid', 'nome', 'cnpj', 'unidade__nome', 'unidade__codigo_eol', )
    list_filter = (
        'unidade__dre',
        'periodo_inicial',
        'unidade__tipo_unidade',
        ('data_de_encerramento', DateRangeFilter),
        'migrada_para_historico_de_membros',
    )
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
    list_display = ('associacao', 'tipo_conta', 'status', 'data_inicio')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('status', 'tipo_conta', 'associacao__unidade__tipo_unidade',
                   'associacao__unidade__dre', ('data_inicio', DateRangeFilter),)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('associacao',)


class AcaoAssociacaoForm(ModelForm):
    def clean(self):
        from .services.acoes_associacoes_service import validate_acao_associacao
        associacao = self.cleaned_data.get('associacao')
        acao = self.cleaned_data.get('acao')

        if associacao is not None and acao is not None:
            try:
                validate_acao_associacao(associacao, acao, self.instance)
            except Exception as error:
                raise ValidationError(error)

        return self.cleaned_data


@admin.register(AcaoAssociacao)
class AcaoAssociacaoAdmin(admin.ModelAdmin):
    form = AcaoAssociacaoForm
    list_display = ('associacao', 'acao', 'status', 'criado_em')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('status', 'acao', 'associacao__unidade__tipo_unidade', 'associacao__unidade__dre',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('associacao',)


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
                'observacao',
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
    list_filter = ('status', 'associacao', 'acao_associacao__acao', 'periodo',
                   'associacao__unidade__tipo_unidade', 'associacao__unidade__dre', 'conta_associacao__tipo_conta')
    list_display_links = ('periodo',)
    readonly_fields = ('saldo_reprogramado_capital', 'saldo_reprogramado_custeio',
                       'saldo_reprogramado_livre', 'uuid', 'id', 'criado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome',)
    fieldsets = (
        (
            None, {
                'fields': (
                    'prestacao_conta',
                    'periodo',
                    'associacao',
                    'conta_associacao',
                    'acao_associacao',
                    'fechamento_anterior',
                    'status',
                    'uuid',
                    'id',
                    'criado_em'
                )
            },
        ),
        (
            'Capital', {
                'fields': (
                    'total_receitas_capital',
                    'total_receitas_devolucao_capital',
                    'total_repasses_capital',
                    'total_despesas_capital',
                    'saldo_reprogramado_capital',
                )
            },
        ),
        (
            'Custeio', {
                'fields': (
                    'total_receitas_custeio',
                    'total_receitas_devolucao_custeio',
                    'total_repasses_custeio',
                    'total_despesas_custeio',
                    'saldo_reprogramado_custeio',
                )
            },
        ),
        (
            'Livre Aplicação', {
                'fields': (
                    'total_receitas_livre',
                    'total_receitas_devolucao_livre',
                    'total_repasses_livre',
                    'saldo_reprogramado_livre',
                )
            },
        ),
        (
            'Especificações de Despesa', {
                'fields': (
                    'especificacoes_despesas_capital',
                    'especificacoes_despesas_custeio',
                )
            },
        ),
        (
            'Receitas não conciliadas', {
                'fields': (
                    'total_receitas_nao_conciliadas_capital',
                    'total_receitas_nao_conciliadas_custeio',
                    'total_receitas_nao_conciliadas_livre'
                )
            },
        ),
        (
            'Despesas não conciliadas', {
                'fields': (
                    'total_despesas_nao_conciliadas_capital',
                    'total_despesas_nao_conciliadas_custeio',
                )
            },
        ),
    )

    raw_id_fields = [
        'prestacao_conta',
        'periodo',
        'associacao',
        'conta_associacao',
        'acao_associacao',
        'fechamento_anterior'
    ]


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
        'associacao',
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
        'consolidado_dre__id',
        'associacao__unidade__tipo_unidade'
    )
    list_display_links = ('get_nome_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__nome')
    raw_id_fields = ('periodo', 'associacao', 'analise_atual', 'consolidado_dre',)

    actions = ['marcar_como_nao_publicada', 'desvincular_pcs_do_consolidado', 'setar_status_anterior_a_retificacao']

    def desvincular_pcs_do_consolidado(self, request, queryset):
        contador = 0
        for prestacao_conta in queryset.all():
            if prestacao_conta.consolidado_dre and not prestacao_conta.publicada:
                contador += 1
                prestacao_conta.consolidado_dre.desvincular_pc_do_consolidado(prestacao_conta)
                prestacao_conta.consolidado_dre = None
                prestacao_conta.save()

        self.message_user(request, f"{contador} PC(s) desvinculada(s)")

    def marcar_como_nao_publicada(self, request, queryset):
        for prestacao_conta in queryset.all():
            if prestacao_conta.publicada and not prestacao_conta.consolidado_dre:
                prestacao_conta.publicada = False
                prestacao_conta.save()

        self.message_user(request, f"PCs marcadas como não publicadas com sucesso!")

    # TODO remover action após solução do bug 100138
    def setar_status_anterior_a_retificacao(self, request, queryset):
        for prestacao_conta in queryset.all():
            if prestacao_conta.status_anterior_a_retificacao:
                prestacao_conta.status = prestacao_conta.status_anterior_a_retificacao
                prestacao_conta.save()

        self.message_user(request, f"PCs setadas ao status anterior da retificação com sucesso!")


@admin.register(Ata)
class AtaAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return f'{obj.associacao.unidade.codigo_eol} - {obj.associacao.unidade.nome}' if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        return obj.periodo.referencia if obj and obj.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    raw_id_fields = ('prestacao_conta', 'associacao', 'composicao', 'presidente_da_reuniao', 'secretario_da_reuniao')

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
        'associacao__unidade__dre'
    )
    list_display_links = ('get_eol_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__unidade__nome',
                     'associacao__unidade__dre__codigo_eol', 'comentarios')


@admin.register(Arquivo)
class ArquivoAdmin(admin.ModelAdmin):
    list_display = ['identificador', 'conteudo', 'tipo_carga', 'status', 'ultima_execucao']
    actions = ['processa_carga', ]
    readonly_fields = ['ultima_execucao', 'status', 'log', 'uuid', 'id']
    list_filter = ['tipo_carga', 'status', ('ultima_execucao', DateRangeFilter), ]
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
    list_display = ('associacao', 'numero_processo', 'ano', 'periodos_str')
    search_fields = ('uuid', 'numero_processo', 'associacao__nome')
    list_filter = ('ano', 'associacao', 'associacao__unidade__tipo_unidade', 'associacao__unidade__dre')
    readonly_fields = ('uuid', 'id')
    filter_horizontal = ('periodos',)
    raw_id_fields = ('associacao',)

    def periodos_str(self, obj):
        """
        Retorna uma string com as referências dos períodos associados ao ProcessoAssociacao.
        """
        return ", ".join([periodo.referencia for periodo in obj.periodos.all()])

    periodos_str.short_description = "Períodos"

@admin.register(ObservacaoConciliacao)
class ObservacaoConciliacaoAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.associacao.unidade.codigo_eol} - {obj.associacao.unidade.nome}' if obj and obj.associacao and obj.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_nome_conta(self, obj):
        return obj.conta_associacao.tipo_conta.nome if obj and obj.conta_associacao else ''

    get_nome_conta.short_description = 'Conta'

    list_display = ('get_unidade', 'periodo', 'get_nome_conta', 'data_extrato',
                    'saldo_extrato', 'texto', 'justificativa_original')
    list_filter = (
        'associacao',
        'conta_associacao__tipo_conta',
        'associacao__unidade__dre',
        'associacao__unidade__tipo_unidade',
        'periodo',
    )
    list_display_links = ('periodo',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('texto', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome')
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
    list_filter = (
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__tipo_unidade',
        'prestacao_conta__associacao__unidade__dre',
    )
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em', )
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')
    raw_id_fields = ['prestacao_conta', ]


@admin.register(AnaliseContaPrestacaoConta)
class AnaliseContaPrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_unidade_codigo_eol(self, obj):
        return obj.prestacao_conta.associacao.unidade.codigo_eol if obj and obj.prestacao_conta and obj.prestacao_conta.associacao and obj.prestacao_conta.associacao.unidade else ''

    get_unidade_codigo_eol.short_description = 'EOL'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    def get_id_analise_prestacao_contas(self, obj):
        return obj.analise_prestacao_conta.id if obj and obj.analise_prestacao_conta and obj.analise_prestacao_conta.id else ''

    get_id_analise_prestacao_contas.short_description = 'Análise de Prestação de contas'

    list_display = (
        'get_unidade_codigo_eol', 'get_associacao',  'get_referencia_periodo', 'data_extrato', 'saldo_extrato', 'get_id_analise_prestacao_contas')
    list_filter = ('prestacao_conta__periodo', 'prestacao_conta__associacao__unidade__dre')
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'prestacao_conta__associacao__unidade__dre__codigo_eol')

    raw_id_fields = ['prestacao_conta', 'analise_prestacao_conta', 'conta_associacao']

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


class DreListFilter(admin.SimpleListFilter):
    from django.utils.translation import gettext_lazy

    title = gettext_lazy('DRE')
    parameter_name = 'dre'

    def lookups(self, request, model_admin):
        dre_set = set()
        for obj in model_admin.get_queryset(request):
            prestacao_conta = obj.prestacao_conta
            associacao = obj.associacao

            if prestacao_conta:
                dre_set.add(prestacao_conta.associacao.unidade.dre)
            elif associacao:
                dre_set.add(associacao.unidade.dre)

        return [(dre.codigo_eol, dre.nome) for dre in dre_set]

    def queryset(self, request, queryset):
        from django.db import models

        if self.value():
            return queryset.filter(
                models.Q(prestacao_conta__associacao__unidade__dre__codigo_eol=self.value()) |
                models.Q(associacao__unidade__dre__codigo_eol=self.value())
            )


@admin.register(ComentarioAnalisePrestacao)
class ComentarioAnalisePrestacaoAdmin(admin.ModelAdmin):
    def get_associacao(self, obj):
        if obj.prestacao_conta:
            return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta.associacao else ''
        elif obj.associacao:
            return obj.associacao.nome
        else:
            return ''

    get_associacao.short_description = 'Associação'

    def get_referencia_periodo(self, obj):
        if obj.prestacao_conta:
            return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta.periodo else ''
        elif obj.periodo:
            return obj.periodo.referencia
        else:
            return ''

    get_referencia_periodo.short_description = 'Período'

    def get_codigo_eol_unidade(self, obj):
        if obj.prestacao_conta and obj.prestacao_conta.associacao and obj.prestacao_conta.associacao.unidade:
            return obj.prestacao_conta.associacao.unidade.codigo_eol
        elif obj.associacao and obj.associacao.unidade:
            return obj.associacao.unidade.codigo_eol
        else:
            return ''

    get_codigo_eol_unidade.short_description = 'EOL'

    list_display = (
        'get_codigo_eol_unidade', 'get_associacao', 'get_referencia_periodo', 'ordem', 'comentario', 'notificado_em')
    list_filter = ('prestacao_conta__periodo', DreListFilter,)
    list_display_links = ('get_associacao',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'ordem', 'comentario', 'prestacao_conta__associacao__unidade__dre__codigo_eol', 'associacao__unidade__dre__codigo_eol', )
    raw_id_fields = ['prestacao_conta', 'associacao', ]


@admin.register(PrevisaoRepasseSme)
class PrevisaoRepasseSmeAdmin(admin.ModelAdmin):
    def get_codigo_eol(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_codigo_eol.short_description = 'EOL'

    list_display = ('get_codigo_eol', 'associacao', 'conta_associacao',
                    'periodo', 'valor_capital', 'valor_custeio', 'valor_livre')
    list_filter = ('associacao', 'periodo', 'conta_associacao__tipo_conta', 'associacao__unidade__dre')
    list_display_links = ('associacao',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__dre__codigo_eol')
    raw_id_fields = ['periodo', 'associacao', 'conta_associacao',]


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

    def get_tempo_notificar_nao_demonstrados(self, obj):
        return obj.tempo_notificar_nao_demonstrados

    get_tempo_notificar_nao_demonstrados.short_description = 'N. Transações não demonstradas (dias)'

    def get_dias_antes_inicio_periodo_pc_para_notificacao(self, obj):
        return obj.dias_antes_inicio_periodo_pc_para_notificacao

    get_dias_antes_inicio_periodo_pc_para_notificacao.short_description = 'N. Inicio do período (dias)'

    def get_dias_antes_fim_periodo_pc_para_notificacao(self, obj):
        return obj.dias_antes_fim_periodo_pc_para_notificacao

    get_dias_antes_fim_periodo_pc_para_notificacao.short_description = 'N. Fim do período (dias)'

    def get_dias_antes_fim_prazo_ajustes_pc_para_notificacao(self, obj):
        return obj.dias_antes_fim_prazo_ajustes_pc_para_notificacao

    get_dias_antes_fim_prazo_ajustes_pc_para_notificacao.short_description = 'N. Fim do prazo de entrega (dias)'

    list_display = [
        '__str__',
        'permite_saldo_conta_negativo',
        'get_tempo_notificar_nao_demonstrados',
        'get_dias_antes_inicio_periodo_pc_para_notificacao',
        'get_dias_antes_fim_periodo_pc_para_notificacao',
        'get_dias_antes_fim_prazo_ajustes_pc_para_notificacao',
    ]

    list_display_links = ['__str__']

    fieldsets = (
        ('Associação', {
            'fields':
                (
                    'permite_saldo_conta_negativo',
                    'permite_saldo_acoes_negativo',
                    'tempo_aguardar_conclusao_pc',
                    'quantidade_tentativas_concluir_pc',
                    'periodo_de_tempo_tentativas_concluir_pc',
                    'tempo_notificar_nao_demonstrados',
                    'dias_antes_inicio_periodo_pc_para_notificacao',
                    'dias_antes_fim_periodo_pc_para_notificacao',
                    'dias_antes_fim_prazo_ajustes_pc_para_notificacao',
                    'numero_periodos_consecutivos',
                    'texto_pagina_valores_reprogramados_ue'
                )
        }),
        ('DRE', {
            'fields': ('texto_pagina_suporte_dre', 'texto_pagina_valores_reprogramados_dre', )
        }),
        ('SME', {
            'fields': ('enviar_email_notificacao', 'texto_pagina_suporte_sme', )
        })
    )


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

    def gerar_pdf_dados_persistidos(self, request, queryset):
        from .services.recuperacao_dados_persistindos_demo_financeiro_service import RecuperaDadosDemoFinanceiro
        from .services.demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf

        for item in queryset:
            if item.dados.exists():
                dados = RecuperaDadosDemoFinanceiro(item).dados_formatados
                gerar_arquivo_demonstrativo_financeiro_pdf(dados, item)

    gerar_pdf_dados_persistidos.short_description = "Gerar PDF Dados Persistidos"

    def regerar_pdf(self, request, queryset):
        from django.contrib.auth import get_user_model

        try:
            usuario = get_user_model().objects.get(username='usr_amcom')
            self.message_user(request, mark_safe(
                "<strong>Atenção! Processo de regeração iniciado. </br> "
                "Este processo rodará em segundo plano e pode demorar! </br> "
            ), level=messages.WARNING)
        except Exception:
            self.message_user(request, mark_safe(
                "<strong>Atenção! Não foi encontrado o usuário 'usr_amcom'. </br> "
                "Portanto não será possível iniciar o processo </br> "
            ), level=messages.WARNING)

        # Data de ocorrencia do bug 109526
        data_inicio = '2023-11-23 00:00:00'
        data_fim = '2023-12-14 23:59:59'

        regerar_demonstrativo_financeiro_async.apply_async(
            (
                data_inicio,
                data_fim,
                'usr_amcom'
            ), countdown=1
        )

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
        'versao',
        ('criado_em', DateRangeFilter),
        'arquivo_pdf_regerado'
    )

    list_display_links = ('get_nome_associacao',)

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    search_fields = (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )

    autocomplete_fields = ['conta_associacao', 'periodo_previa', 'prestacao_conta']

    actions = ['gerar_pdf_dados_persistidos', 'regerar_pdf']


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

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    search_fields = (
        'prestacao_conta__associacao__unidade__codigo_eol',
        'prestacao_conta__associacao__unidade__nome',
        'prestacao_conta__associacao__nome'
    )

    autocomplete_fields = ['conta_associacao', 'periodo_previa', 'prestacao_conta']

    actions = ['gerar_pdf']

    def gerar_pdf(self, request, queryset):
        from .services.relacao_bens import gerar_arquivo_relacao_de_bens_dados_persistidos
        for item in queryset:
            gerar_arquivo_relacao_de_bens_dados_persistidos(item)


class ItemRelatorioRelacaoDeBensInline(admin.TabularInline):
    extra = 0
    model = ItemRelatorioRelacaoDeBens


@admin.register(RelatorioRelacaoBens)
class RelatorioRelacaoBensAdmin(admin.ModelAdmin):
    inlines = [ItemRelatorioRelacaoDeBensInline]
    list_display = ('nome_associacao', 'conta', 'periodo_referencia', 'criado_em', )
    fieldsets = [('Cabeçalho', {
        "fields": ["periodo_referencia", "periodo_data_inicio", "periodo_data_fim", "conta"],
    }),
        ('Identificação APM', {
            "fields": ["tipo_unidade", "nome_unidade", "nome_associacao", "cnpj_associacao", "codigo_eol_associacao", "nome_dre_associacao",
                       "presidente_diretoria_executiva",  "cargo_substituto_presidente_ausente"],
        }),
        ('Valor', {
            "fields": ["valor_total"],
        }),
        ("Informações adicionais", {
            "fields": ['relacao_bens', 'usuario', 'data_geracao', 'uuid', 'id', 'criado_em', 'alterado_em']
        }),]

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    search_fields = [
        'nome_associacao',
        'codigo_eol_associacao',
    ]

    list_filter = (
        'relacao_bens__conta_associacao__tipo_conta',
        'relacao_bens__prestacao_conta__periodo',
        'relacao_bens__periodo_previa'
    )


@admin.register(MembroAssociacao)
class MembroAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo_associacao', 'associacao')
    search_fields = (
        'nome', 'codigo_identificacao', 'uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome',
        'associacao__nome', 'cpf', )
    list_filter = (
        'associacao',
        'cargo_associacao',
        'representacao',
        'associacao__unidade__tipo_unidade',
        'associacao__unidade__dre',
    )
    readonly_fields = ('uuid', 'id')
    autocomplete_fields = ['associacao', ]


@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('prefixo', 'nome')


@admin.register(ArquivoDownload)
class ArquivoDownloadAdmin(admin.ModelAdmin):
    list_display = ('identificador', 'status', 'alterado_em', 'lido', 'informacoes')
    readonly_fields = ('uuid', 'id',)
    list_display_links = ('identificador',)


@admin.register(AnalisePrestacaoConta)
class AnalisePrestacaoContaAdmin(admin.ModelAdmin):

    def get_associacao(self, obj):
        return obj.prestacao_conta.associacao.nome if obj and obj.prestacao_conta and obj.prestacao_conta.associacao else ''

    get_associacao.short_description = 'Associação'

    def get_unidade(self, obj):
        return f'{obj.prestacao_conta.associacao.unidade.codigo_eol} - {obj.prestacao_conta.associacao.unidade.nome}' if obj and obj.prestacao_conta and obj.prestacao_conta.associacao and obj.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = ('get_unidade', 'get_referencia_periodo', 'criado_em', 'status',)
    list_filter = (
        'prestacao_conta__periodo',
        'prestacao_conta__associacao__unidade__tipo_unidade',
        'prestacao_conta__associacao__unidade__dre',
        'status',
        'status_versao',
        'versao',
        'status_versao_apresentacao_apos_acertos',
        'versao_pdf_apresentacao_apos_acertos',
    )
    list_display_links = ('get_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome')
    raw_id_fields = ['prestacao_conta', 'devolucao_prestacao_conta', ]


@admin.register(AnaliseLancamentoPrestacaoConta)
class AnaliseLancamentoPrestacaoContaAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol} - {obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}' if obj and obj.analise_prestacao_conta and obj.analise_prestacao_conta.prestacao_conta and obj.analise_prestacao_conta.prestacao_conta.associacao and obj.analise_prestacao_conta.prestacao_conta.associacao.unidade else '-'

    get_unidade.short_description = 'Unidade'

    def get_periodo(self, obj):
        return f'{obj.analise_prestacao_conta.prestacao_conta.periodo.referencia}' if obj and obj.analise_prestacao_conta and obj.analise_prestacao_conta.prestacao_conta and obj.analise_prestacao_conta.prestacao_conta.periodo else ''

    get_periodo.short_description = 'Período'

    def get_analise_pc(self, obj):
        return f'#{obj.analise_prestacao_conta.pk}' if obj and obj.analise_prestacao_conta else ''

    get_analise_pc.short_description = 'Análise PC'

    list_display = ['get_unidade', 'get_periodo', 'get_analise_pc', 'tipo_lancamento', 'resultado', 'status_realizacao',
                    'devolucao_tesouro_atualizada']
    list_filter = (
        # 'analise_corrigida_via_admin_action', # TODO remover esse filtro quando não for mais necessário
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__tipo_unidade',
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__dre',
        'analise_prestacao_conta__prestacao_conta__periodo',
        'tipo_lancamento',
        'devolucao_tesouro_atualizada',
    )

    search_fields = (
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'analise_prestacao_conta__prestacao_conta__associacao__nome',
        'analise_prestacao_conta__uuid'
    )

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    raw_id_fields = ['analise_prestacao_conta', 'despesa', 'receita', 'analise_prestacao_conta_auxiliar']

    # TODO remover actions quando não forem mais necessárias
    # actions = ['inativar_analises_lancamento_prestacao_conta_duplicadas_gasto',
    #            'inativar_analises_lancamento_prestacao_conta_duplicadas_receita',
    #            'reverter_inativar_analises_lancamento_prestacao_conta_duplicadas_gasto',
    #            'reverter_inativar_analises_lancamento_prestacao_conta_duplicadas_receita']

    def inativar_analises_lancamento_prestacao_conta_duplicadas_gasto(self, request, queryset):
        contador = 0

        result_gasto = AnaliseLancamentoPrestacaoConta.objects.filter(tipo_lancamento='GASTO').values(
            'analise_prestacao_conta_id', 'tipo_lancamento', 'despesa_id').annotate(dcount=Count('despesa_id')).filter(
            dcount__gt=1).order_by('analise_prestacao_conta_id')

        for registro in result_gasto:

            primeira_analise = AnaliseLancamentoPrestacaoConta.objects.filter(
                analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                tipo_lancamento=registro['tipo_lancamento'],
                despesa_id=registro['despesa_id'],
            ).exclude(status_realizacao='PENDENTE').order_by('id').first()

            if not primeira_analise:
                primeira_analise = AnaliseLancamentoPrestacaoConta.objects.filter(
                    analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                    tipo_lancamento=registro['tipo_lancamento'],
                    despesa_id=registro['despesa_id']
                ).order_by('id').first()

            todas_analises_da_despesa = AnaliseLancamentoPrestacaoConta.objects.filter(
                analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                tipo_lancamento=registro['tipo_lancamento'],
                despesa_id=registro['despesa_id']
            )

            for analise in todas_analises_da_despesa:

                if analise == primeira_analise:
                    logging.info(
                        f'**************** Primeira Analise PC ID: {primeira_analise.analise_prestacao_conta_id} Despesa ID: {primeira_analise.despesa_id}  Status Realizacao: {primeira_analise.status_realizacao} | Análise Atual PC ID: {analise.analise_prestacao_conta_id} Despesa ID: {analise.despesa_id} Status Realizacao: {analise.status_realizacao}')
                    continue

                if not analise.analise_corrigida_via_admin_action:
                    logging.info(
                        f"**************** Demais Analise PC ID: {analise.analise_prestacao_conta_id} Despesa ID: {analise.despesa_id} Status Realizacao: {analise.status_realizacao}")
                    analise.analise_prestacao_conta_auxiliar = analise.analise_prestacao_conta
                    analise.analise_corrigida_via_admin_action = True
                    analise.analise_prestacao_conta = None
                    analise.save()

                    contador += 1

        logging.info(f"**************** Total de registros: {contador}")
        self.message_user(request, f"{contador} Análise de lançamentos do tipo GASTO inativadas.")

    def reverter_inativar_analises_lancamento_prestacao_conta_duplicadas_gasto(self, request, queryset):
        contador = 0

        result_gasto = AnaliseLancamentoPrestacaoConta.objects.filter(
            tipo_lancamento='GASTO',
            analise_corrigida_via_admin_action=True,
            analise_prestacao_conta__isnull=True,
            analise_prestacao_conta_auxiliar__isnull=False
        )

        for analise in result_gasto:
            analise.analise_prestacao_conta = analise.analise_prestacao_conta_auxiliar
            analise.analise_prestacao_conta_auxiliar = None
            analise.analise_corrigida_via_admin_action = False
            analise.save()

            logging.info(
                f"**************** Revertendo Inativação da Analise de Lançamento Tipo Gasto: {analise} Despesa ID: {analise.despesa_id}")

            contador += 1

        logging.info(f"**************** Total de registros: {contador}")
        self.message_user(request, f"{contador} Inativações de Análise de lançamentos do tipo GASTO revertidas.")

    def inativar_analises_lancamento_prestacao_conta_duplicadas_receita(self, request, queryset):
        contador = 0

        result_receita = AnaliseLancamentoPrestacaoConta.objects.filter(tipo_lancamento='CREDITO')\
            .values('analise_prestacao_conta_id', 'tipo_lancamento', 'receita_id')\
            .annotate(dcount=Count('receita_id'))\
            .filter(dcount__gt=1)\
            .order_by('analise_prestacao_conta_id')

        for registro in result_receita:

            primeira_analise = AnaliseLancamentoPrestacaoConta.objects.filter(
                analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                tipo_lancamento=registro['tipo_lancamento'],
                receita_id=registro['receita_id']
            ).exclude(status_realizacao='PENDENTE').order_by('id').first()

            if not primeira_analise:
                primeira_analise = AnaliseLancamentoPrestacaoConta.objects.filter(
                    analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                    tipo_lancamento=registro['tipo_lancamento'],
                    receita_id=registro['receita_id']
                ).order_by('id').first()

            todas_analises_da_receita = AnaliseLancamentoPrestacaoConta.objects.filter(
                analise_prestacao_conta_id=registro['analise_prestacao_conta_id'],
                tipo_lancamento=registro['tipo_lancamento'],
                receita_id=registro['receita_id']
            )

            for analise in todas_analises_da_receita:
                if analise == primeira_analise:
                    logging.info(
                        f'**************** Primeira Analise PC ID: {primeira_analise.analise_prestacao_conta_id} Receita ID: {primeira_analise.receita_id}  Status Realizacao: {primeira_analise.status_realizacao} | Análise Atual PC ID: {analise.analise_prestacao_conta_id} Receita ID: {analise.receita_id} Status Realizacao: {analise.status_realizacao}')
                    continue

                if not analise.analise_corrigida_via_admin_action:
                    logging.info(
                        f"**************** Demais Analise PC ID: {analise.analise_prestacao_conta_id} Receita ID: {analise.receita_id} Status Realizacao: {analise.status_realizacao}")
                    analise.analise_prestacao_conta_auxiliar = analise.analise_prestacao_conta
                    analise.analise_corrigida_via_admin_action = True
                    analise.analise_prestacao_conta = None
                    analise.save()
                    contador += 1

        logging.info(f"**************** Total de registros: {contador}")
        self.message_user(request, f"{contador} Análise de lançamentos do tipo RECEITA inativadas.")

    def reverter_inativar_analises_lancamento_prestacao_conta_duplicadas_receita(self, request, queryset):
        contador = 0

        result_receita = AnaliseLancamentoPrestacaoConta.objects.filter(
            tipo_lancamento='CREDITO',
            analise_corrigida_via_admin_action=True,
            analise_prestacao_conta__isnull=True,
            analise_prestacao_conta_auxiliar__isnull=False
        )

        for analise in result_receita:
            analise.analise_prestacao_conta = analise.analise_prestacao_conta_auxiliar
            analise.analise_prestacao_conta_auxiliar = None
            analise.analise_corrigida_via_admin_action = False
            analise.save()

            logging.info(
                f"**************** Revertendo Inativação da Analise de Lançamento Tipo Receita: {analise} Receita ID: {analise.receita_id}")

            contador += 1

        logging.info(f"**************** Total de registros: {contador}")
        self.message_user(request, f"{contador} Inativações de Análise de lançamentos do tipo RECEITA revertidas.")


@admin.register(TipoAcertoLancamento)
class TipoAcertoLancamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'ativo']
    search_fields = ['nome', 'categoria']
    list_filter = ['nome', 'categoria', 'ativo']
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(SolicitacaoAcertoLancamento)
class SolicitacaoAcertoLancamentoAdmin(admin.ModelAdmin):
    raw_id_fields = ['analise_lancamento', 'tipo_acerto', 'devolucao_ao_tesouro']

    def get_unidade(self, obj):
        return f'{obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol} - {obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.tipo_unidade} - {obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}' if obj and obj.analise_lancamento and obj.analise_lancamento.analise_prestacao_conta and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def tipo_lancamento(self, obj):
        return obj.analise_lancamento.tipo_lancamento if obj and obj.analise_lancamento else ''

    tipo_lancamento.short_description = 'Tipo Lançamento'

    def get_despesa(self, obj):
        return obj.analise_lancamento.despesa if obj and obj.analise_lancamento else ''

    get_despesa.short_description = 'Despesa'

    def get_periodo(self, obj):
        return f'{obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo.referencia}' if obj and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta and obj.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo else ''

    get_periodo.short_description = 'Período'

    def get_analise_pc(self, obj):
        return f'#{obj.analise_lancamento.analise_prestacao_conta.pk}' if obj and obj.analise_lancamento.analise_prestacao_conta else ''

    get_analise_pc.short_description = 'Análise PC'

    list_display = ['analise_lancamento', 'get_unidade', 'get_periodo', 'get_analise_pc',
                    'tipo_acerto', 'tipo_lancamento', 'devolucao_ao_tesouro', 'get_despesa', 'copiado']
    search_fields = [
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'detalhamento',
    ]
    list_filter = [
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo',
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__tipo_unidade',
        'analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__dre',
        'analise_lancamento__tipo_lancamento',
        'tipo_acerto',
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
    def get_unidade(self, obj):
        return f'{obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol} - {obj.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}' if obj and obj.analise_prestacao_conta.prestacao_conta and obj.analise_prestacao_conta.prestacao_conta.associacao and obj.analise_prestacao_conta.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_periodo(self, obj):
        return f'{obj.analise_prestacao_conta.prestacao_conta.periodo.referencia}' if obj and obj.analise_prestacao_conta.prestacao_conta and obj.analise_prestacao_conta.prestacao_conta.periodo else ''

    get_periodo.short_description = 'Período'

    def get_analise_pc(self, obj):
        return f'#{obj.analise_prestacao_conta.pk}' if obj and obj.analise_prestacao_conta else ''

    get_analise_pc.short_description = 'Análise PC'
    list_display = ['get_unidade', 'get_periodo', 'get_analise_pc',
                    'tipo_documento_prestacao_conta', 'resultado', 'status_realizacao']
    list_filter = [
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__tipo_unidade',
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__dre',
        'analise_prestacao_conta__prestacao_conta__periodo',
        'tipo_documento_prestacao_conta',
    ]

    search_fields = (
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'analise_prestacao_conta__prestacao_conta__associacao__nome',
    )

    readonly_fields = ('uuid', 'id',)

    autocomplete_fields = ['analise_prestacao_conta', 'conta_associacao']


@admin.register(SolicitacaoAcertoDocumento)
class SolicitacaoAcertoDocumentoAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol} - {obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao.unidade.nome}' if obj and obj.analise_documento and obj.analise_documento.analise_prestacao_conta and obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao and obj.analise_documento.analise_prestacao_conta.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_despesa(self, obj):
        return obj.analise_documento.despesa if obj and obj.analise_documento else ''

    get_despesa.short_description = 'Despesa'

    def get_periodo(self, obj):
        return f'{obj.analise_documento.analise_prestacao_conta.prestacao_conta.periodo.referencia}' if obj and obj.analise_documento.analise_prestacao_conta.prestacao_conta and obj.analise_documento.analise_prestacao_conta.prestacao_conta.periodo else ''

    get_periodo.short_description = 'Período'

    def get_analise_pc(self, obj):
        return f'#{obj.analise_documento.analise_prestacao_conta.pk}' if obj and obj.analise_documento.analise_prestacao_conta else ''

    get_analise_pc.short_description = 'Análise PC'
    list_display = ['get_unidade', 'get_periodo', 'get_analise_pc', 'tipo_acerto', 'copiado',]
    search_fields = [
        'analise_documento__analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'analise_documento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
    ]
    list_filter = [
        'analise_documento__analise_prestacao_conta__prestacao_conta__periodo',
        'analise_documento__analise_prestacao_conta__prestacao_conta__associacao__unidade__tipo_unidade',
        'analise_documento__analise_prestacao_conta__prestacao_conta__associacao__unidade__dre',
        'tipo_acerto',
        'copiado'
    ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em',)

    raw_id_fields = ['analise_documento', 'despesa_incluida', 'receita_incluida']


@admin.register(Participante)
class PresenteAtaAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.ata.associacao.unidade.codigo_eol} - {obj.ata.associacao.unidade.nome}' if obj and obj.ata and obj.ata.associacao and obj.ata.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_periodo(self, obj):
        return f'{obj.ata.periodo.referencia}' if obj and obj.ata and obj.ata.periodo else ''

    get_periodo.short_description = 'Período'

    list_display = ['get_unidade', 'get_periodo', 'ata', 'identificacao', 'nome', 'cargo', 'membro']

    search_fields = [
        'nome',
        'identificacao',
        'ata__associacao__unidade__codigo_eol',
        'ata__associacao__unidade__nome',
    ]
    list_filter = [
        'ata__periodo',
        'ata__associacao__unidade__tipo_unidade',
        'ata__associacao__unidade__dre',
        'cargo',
        'membro',
        ('criado_em', DateRangeFilter),
        ('alterado_em', DateRangeFilter),
    ]
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('ata',)


@admin.register(ValoresReprogramados)
class ValoresReprogramadosAdmin(admin.ModelAdmin):
    def get_unidade(self, obj):
        return f'{obj.associacao.unidade.codigo_eol} - {obj.associacao.unidade.nome}' if obj and obj.associacao and obj.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_tipo_conta(self, obj):
        return f'{obj.conta_associacao.tipo_conta.nome}' if obj and obj.conta_associacao and obj.conta_associacao.tipo_conta else ''

    get_tipo_conta.short_description = 'Conta'

    def get_acao(self, obj):
        return f'{obj.acao_associacao.acao.nome}' if obj and obj.acao_associacao and obj.acao_associacao.acao else ''

    get_acao.short_description = 'Ação'

    list_display = ('get_unidade', 'get_tipo_conta', 'get_acao', 'aplicacao_recurso', 'valor_ue', 'valor_dre')
    search_fields = ('uuid', 'associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = (
        'associacao',
        'associacao__unidade',
        'associacao__unidade__tipo_unidade',
        'associacao__unidade__dre',
        'associacao__status_valores_reprogramados',
        'associacao__periodo_inicial',
        'conta_associacao__tipo_conta',
        'acao_associacao__acao',
        'aplicacao_recurso'
    )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('associacao', 'periodo', 'conta_associacao', 'acao_associacao',)


@admin.register(DevolucaoAoTesouro)
class DevolucaoAoTesouroAdmin(admin.ModelAdmin):
    raw_id_fields = ['despesa']

    def get_dre(self, obj):
        return obj.prestacao_conta.associacao.unidade.dre.nome

    get_dre.short_description = 'DRE'

    def get_unidade(self, obj):
        return f'{obj.prestacao_conta.associacao.unidade.codigo_eol} - {obj.prestacao_conta.associacao.unidade.nome}' if obj and obj.prestacao_conta and obj.prestacao_conta.associacao and obj.prestacao_conta.associacao.unidade else ''

    get_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        return obj.prestacao_conta.periodo.referencia if obj and obj.prestacao_conta and obj.prestacao_conta.periodo else ''

    get_referencia_periodo.short_description = 'Período'

    list_display = (
        'get_dre', 'get_unidade', 'get_referencia_periodo', 'despesa', 'data', 'tipo', 'devolucao_total', 'valor', 'visao_criacao')

    list_filter = (
        'prestacao_conta__periodo',
        'tipo',
        'devolucao_total',
        'visao_criacao',
        'data',
        'prestacao_conta__associacao__unidade__dre'
    )

    list_display_links = ('get_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('prestacao_conta__associacao__unidade__codigo_eol', 'prestacao_conta__associacao__unidade__nome',
                     'prestacao_conta__associacao__nome', 'motivo')

    autocomplete_fields = ['prestacao_conta']


@admin.register(SolicitacaoDevolucaoAoTesouro)
class SolicitacaoDevolucaoPrestacaoContaAdmin(admin.ModelAdmin):
    raw_id_fields = ['solicitacao_acerto_lancamento']

    def get_unidade(self, obj):
        if (
            obj and
            obj.solicitacao_acerto_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade
        ):
            unidade = obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.associacao.unidade
            return f'{unidade.codigo_eol} - {unidade.nome}'
        else:
            return ''
    get_unidade.short_description = 'Unidade'

    def get_referencia_periodo(self, obj):
        if (
            obj and
            obj.solicitacao_acerto_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta and
            obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo
        ):
            periodo = obj.solicitacao_acerto_lancamento.analise_lancamento.analise_prestacao_conta.prestacao_conta.periodo
            return periodo.referencia
        else:
            return ''

    get_referencia_periodo.short_description = 'Período'

    def get_despesa(self, obj):
        if (
            obj and
            obj.solicitacao_acerto_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento and
            obj.solicitacao_acerto_lancamento.analise_lancamento.despesa
        ):
            return obj.solicitacao_acerto_lancamento.analise_lancamento.despesa
        else:
            return ''

    get_despesa.short_description = 'Despesa'

    list_display = ('get_unidade', 'get_referencia_periodo', 'get_despesa', 'tipo', 'valor', 'devolucao_total')
    list_filter = (
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__dre',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__tipo_unidade',
        'tipo',
        'devolucao_total',
    )
    list_display_links = ('get_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em')
    search_fields = (
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome',
        'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__nome',
        'motivo'
    )


@admin.register(FalhaGeracaoPc)
class FalhaGeracaoPcAdmin(admin.ModelAdmin):
    list_display = ['ultimo_usuario', 'associacao', 'periodo', 'data_hora_ultima_ocorrencia',
                    'qtd_ocorrencias_sucessivas', 'resolvido']
    list_filter = ['ultimo_usuario', 'associacao', 'periodo', 'data_hora_ultima_ocorrencia',
                   'qtd_ocorrencias_sucessivas', 'resolvido', 'associacao__unidade__dre']
    readonly_fields = ('uuid', 'id')
    search_fields = ('ultimo_usuario__username', 'associacao__nome', 'associacao__unidade__nome')


@admin.register(TransferenciaEol)
class TransferenciaEolAdmin(admin.ModelAdmin):
    def transfere_codigo_eol(self, request, queryset):
        for transferencia in queryset.all():
            transferencia.transferir()

        self.message_user(request, f"Transferência concluida.")

    list_display = ('eol_transferido', 'eol_historico', 'tipo_nova_unidade',
                    'tipo_conta_transferido', 'data_inicio_atividades', 'status_processamento')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em', 'log_execucao')
    actions = [transfere_codigo_eol]


@admin.register(TaskCelery)
class TaskCeleryAdmin(admin.ModelAdmin):
    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    list_display = [
        'get_eol_unidade',
        'nome_task',
        'associacao',
        'periodo',
        'id_task_assincrona',
        'finalizada',
    ]
    readonly_fields = ('uuid', 'id_task_assincrona', 'nome_task', 'log', 'criado_em', 'alterado_em', )
    raw_id_fields = ('usuario', 'associacao', 'prestacao_conta', 'periodo',)

    search_fields = [
        'nome_task',
        'associacao__unidade__codigo_eol',
        'associacao__unidade__nome',
        'associacao__nome',
        'usuario__username'
    ]

    list_filter = [
        'finalizada',
        'finalizacao_forcada',
        ('criado_em', DateRangeFilter),
        ('alterado_em', DateRangeFilter),
        ('data_hora_finalizacao', DateRangeFilter),
    ]


class ItemResumoPorAcaoInLine(admin.TabularInline):
    model = ItemResumoPorAcao
    extra = 1  # Quantidade de linhas que serão exibidas.
    classes = ('collapse', )


class ItemCreditoInLine(admin.TabularInline):
    model = ItemCredito
    extra = 1  # Quantidade de linhas que serão exibidas.
    classes = ('collapse', )


class ItemDespesaInLine(admin.TabularInline):
    model = ItemDespesa
    extra = 1  # Quantidade de linhas que serão exibidas.
    classes = ('collapse', )


@admin.register(DadosDemonstrativoFinanceiro)
class DadosDemonstrativoFinanceiroAdmin(admin.ModelAdmin):
    list_display = ['nome_associacao', 'conta_associacao', 'periodo_referencia', 'criado_em']
    list_filter = (
        'demonstrativo__conta_associacao__tipo_conta',
        'demonstrativo__prestacao_conta__periodo',
        'demonstrativo__periodo_previa',
        'demonstrativo__conta_associacao__associacao__unidade__dre'
    )

    search_fields = [
        'nome_associacao',
        'codigo_eol_associacao',
        'demonstrativo__conta_associacao__associacao__unidade__dre__codigo_eol'
    ]

    fieldsets = [
        ('Demonstrativo Financeiro', {
            "fields": [
                "demonstrativo",
            ],
        }),
        ('Cabeçalho', {
            "fields": [
                "periodo_referencia",
                "periodo_data_inicio",
                "periodo_data_fim",
                "conta_associacao",
            ],
        }),
        ('Identificação da Associação', {
            "fields": [
                "nome_associacao",
                "cnpj_associacao",
                "nome_dre_associacao",
                "codigo_eol_associacao",
                "cargo_substituto_presidente_ausente",
                "presidente_diretoria_executiva",
                "presidente_conselho_fiscal",
            ],
        }),
        ('Identificação da Associação', {
            "fields": [
                "banco",
                "agencia",
                "conta",
                "data_extrato",
                "saldo_extrato",
                "conta_encerrada_em"
            ],
        }),
        ('Justificativa', {
            "fields": [
                "justificativa_info_adicionais",
            ],
        }),
        ('Rodapé', {
            "fields": [
                "tipo_unidade",
                "nome_unidade",
                "texto_rodape",
                "data_geracao",
            ],
        }),
        ('Totais', {
            "fields": [
                "total_creditos",
                "total_despesas_demonstradas",
                "total_despesas_nao_demonstradas",
                "total_despesas_nao_demonstradas_periodos_anteriores",
            ],
        }),
        ('Informações Adicionais', {
            "fields": [
                "id",
                "uuid",
                "criado_em",
                "alterado_em",
            ],
        }),
    ]

    inlines = [ItemResumoPorAcaoInLine, ItemCreditoInLine, ItemDespesaInLine]
    raw_id_fields = ('demonstrativo', )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')


@admin.register(PrestacaoContaReprovadaNaoApresentacao)
class PrestacaoContaReprovadaNaoApresentacaoAdmin(admin.ModelAdmin):

    def get_eol_unidade(self, obj):
        return obj.associacao.unidade.codigo_eol if obj and obj.associacao and obj.associacao.unidade else ''

    get_eol_unidade.short_description = 'EOL'

    def get_nome_unidade(self, obj):
        return obj.associacao.unidade.nome if obj and obj.associacao and obj.associacao.unidade else ''

    get_nome_unidade.short_description = 'Unidade Educacional'

    def get_periodo_referencia(self, obj):
        return obj.periodo.referencia if obj.periodo else ""

    get_periodo_referencia.short_description = 'Período'

    list_display = (
        'get_eol_unidade',
        'get_nome_unidade',
        'associacao',
        'get_periodo_referencia',
        'data_de_reprovacao',
    )

    list_filter = (
        'associacao__unidade__dre',
        'associacao',
        'periodo',
        'associacao__unidade__tipo_unidade'
    )

    list_display_links = ('get_nome_unidade',)
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__nome')
    raw_id_fields = ('periodo', 'associacao',)
