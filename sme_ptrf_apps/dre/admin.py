import logging

from django.contrib import admin, messages

from .models import (
    Atribuicao, GrupoVerificacaoRegularidade, ListaVerificacaoRegularidade,
    ItemVerificacaoRegularidade,
    VerificacaoRegularidadeAssociacao, TecnicoDre, FaqCategoria, Faq, RelatorioConsolidadoDRE,
    JustificativaRelatorioConsolidadoDRE, ObsDevolucaoRelatorioConsolidadoDRE,
    ParametroFiqueDeOlhoRelDre, MotivoAprovacaoRessalva, MotivoReprovacao, Comissao, MembroComissao,
    AnoAnaliseRegularidade, AnaliseRegularidadeAssociacao, ParametrosDre, AtaParecerTecnico,
    PresenteAtaDre, ConsolidadoDRE, Lauda, DocumentoAdicional, ComentarioAnaliseConsolidadoDRE, AnaliseConsolidadoDre,
    AnaliseDocumentoConsolidadoDre
)

admin.site.register(ParametroFiqueDeOlhoRelDre)
admin.site.register(MotivoAprovacaoRessalva)
admin.site.register(MotivoReprovacao)
admin.site.register(ParametrosDre)

logger = logging.getLogger(__name__)


class ListasVerificacaoInline(admin.TabularInline):
    extra = 1
    model = ListaVerificacaoRegularidade


class ItensVerificacaoInline(admin.TabularInline):
    extra = 1
    model = ItemVerificacaoRegularidade


@admin.register(Lauda)
class LaudaAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'status', 'consolidado_dre')
    list_filter = ('status', 'dre', 'periodo', 'tipo_conta', 'consolidado_dre')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome',)
    actions = ['vincular_consolidado_dre', ]

    def vincular_consolidado_dre(self, request, queryset):
        from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

        for lauda in queryset.all():
            VincularConsolidadoService.vincular_artefato(lauda)

        self.message_user(request, f"Laudas vinculadas com sucesso!")


@admin.register(ConsolidadoDRE)
class ConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    list_display = (
        'get_nome_dre',
        'periodo',
        'status',
        'versao',
        'eh_parcial',
        'sequencia_de_publicacao',
        'sequencia_de_retificacao',
        'status_sme',
        'data_publicacao',
        'pagina_publicacao',
        'responsavel_pela_analise',
    )
    list_filter = ('status', 'dre', 'periodo', 'versao', 'status_sme', 'responsavel_pela_analise')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id', 'pcs_do_consolidado', 'criado_em', 'alterado_em', )
    search_fields = ('dre__nome',)

    actions = ('vincular_pcs_faltantes',)

    # TODO remover action após solução do bug 100138
    def vincular_pcs_faltantes(self, request, queryset):
        from sme_ptrf_apps.core.models import PrestacaoConta

        for consolidado in queryset.all():
            dre = consolidado.dre
            periodo = consolidado.periodo
            pcs_do_consolidado = consolidado.pcs_do_consolidado.all()

            pcs_dessa_dre_e_periodo = PrestacaoConta.objects.filter(
                periodo=periodo, associacao__unidade__dre=dre, consolidado_dre=consolidado).all()

            if pcs_do_consolidado.count() == pcs_dessa_dre_e_periodo.count():
                continue

            for pc in pcs_dessa_dre_e_periodo:
                if pc not in pcs_do_consolidado:
                    consolidado.pcs_do_consolidado.add(pc)

        self.message_user(request, f"Prestações faltantes vinculadas com sucesso!")


@admin.register(GrupoVerificacaoRegularidade)
class GrupoVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', ]
    search_fields = ['titulo', ]
    readonly_fields = ['id', 'uuid']
    inlines = [
        ListasVerificacaoInline
    ]


@admin.register(ListaVerificacaoRegularidade)
class ListaVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'grupo', 'id']
    search_fields = ['titulo', ]
    readonly_fields = ['id', 'uuid']
    inlines = [
        ItensVerificacaoInline
    ]
    list_filter = ('grupo',)


@admin.register(ItemVerificacaoRegularidade)
class ItemVerificacaoRegularidadeAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'lista')
    search_fields = ('uuid', 'descricao')
    list_filter = ('lista', 'lista__grupo')
    readonly_fields = ('uuid', 'id')


@admin.register(TecnicoDre)
class TecnicoDreAdmin(admin.ModelAdmin):
    list_display = ('rf', 'nome', 'dre', 'telefone', 'email')
    search_fields = ('uuid', 'nome', 'rf')
    list_filter = ('dre',)
    readonly_fields = ('uuid', 'id')


@admin.register(FaqCategoria)
class ListaFaqCategorias(admin.ModelAdmin):
    list_display = ('id', 'nome',)
    list_display_links = ('id', 'nome')
    fields = ['nome', 'uuid']
    readonly_fields = ('uuid', 'id')


@admin.register(Faq)
class ListaFaq(admin.ModelAdmin):
    list_display = ('id', 'pergunta', 'resposta', 'categoria',)
    list_display_links = ('id', 'pergunta')
    list_filter = ('categoria',)
    fields = ['pergunta', 'resposta', 'categoria', 'uuid']
    readonly_fields = ('uuid', 'id')


@admin.register(Atribuicao)
class AtribuicaoAdmin(admin.ModelAdmin):
    list_display = ('codigo_eol_unidade', 'nome_unidade', 'nome_tecnico', 'periodo')
    list_filter = ('unidade__dre', 'periodo')
    search_fields = ('unidade__codigo_eol','unidade__nome', 'tecnico__nome', 'tecnico__rf')
    raw_id_fields = ('tecnico', 'unidade')
    def nome_tecnico(self, obj):
        return obj.tecnico.nome if obj.tecnico else ''

    def codigo_eol_unidade(self, obj):
        return obj.unidade.codigo_eol if obj.unidade else ''

    def nome_unidade(self, obj):
        return obj.unidade.nome if obj.unidade else ''


@admin.register(RelatorioConsolidadoDRE)
class RelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'status', 'versao', 'consolidado_dre')
    list_filter = ('status', 'dre', 'periodo', 'tipo_conta', 'consolidado_dre')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome',)

    actions = ['vincular_consolidado_dre', ]

    def vincular_consolidado_dre(self, request, queryset):
        from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

        for relatorio in queryset.all():
            VincularConsolidadoService.vincular_artefato(relatorio)

        self.message_user(request, f"Relatórios vinculados com sucesso!")


@admin.register(JustificativaRelatorioConsolidadoDRE)
class JustificativaRelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'texto', 'consolidado_dre')
    list_filter = ('dre', 'periodo', 'tipo_conta', 'consolidado_dre')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome', 'texto')


@admin.register(ObsDevolucaoRelatorioConsolidadoDRE)
class JObsDevolucaoRelatorioConsolidadoDREAdmin(admin.ModelAdmin):

    def get_nome_dre(self, obj):
        return obj.dre.nome if obj and obj.dre else ''

    get_nome_dre.short_description = 'DRE'

    def get_nome_tipo_conta(self, obj):
        return obj.tipo_conta.nome if obj and obj.tipo_conta else ''

    get_nome_tipo_conta.short_description = 'Tipo de conta'

    list_display = ('get_nome_dre', 'periodo', 'get_nome_tipo_conta', 'tipo_devolucao', 'observacao')
    list_filter = (
        'dre', 'periodo', 'tipo_conta', 'tipo_devolucao', 'tipo_devolucao_a_conta', 'tipo_devolucao_ao_tesouro')
    list_display_links = ('get_nome_dre',)
    readonly_fields = ('uuid', 'id')
    search_fields = ('dre__nome', 'observacao')


@admin.register(Comissao)
class ComissaoAdmin(admin.ModelAdmin):

    def get_e_exame_de_contas(self, obj):
        comissao_exame_contas = ParametrosDre.objects.first().comissao_exame_contas if ParametrosDre.objects.exists() else None
        return "X" if obj == comissao_exame_contas else ""

    get_e_exame_de_contas.short_description = 'Exame de contas'

    list_display = ['nome', 'get_e_exame_de_contas']
    search_fields = ['nome', ]
    readonly_fields = ['id', 'uuid', 'criado_em', 'alterado_em']

    actions = ['define_como_exame_de_contas', ]

    def define_como_exame_de_contas(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas uma comissão para ser a de exame de contas.",
                              level=messages.ERROR)
            return

        comissao = queryset.first()
        parametros_dre = ParametrosDre.get()
        parametros_dre.comissao_exame_contas = comissao
        parametros_dre.save()

        self.message_user(
            request,
            f"Comissão {comissao.nome} definida como exame de contas nos parâmetros da DRE.",
        )


@admin.register(MembroComissao)
class MembroComissaoAdmin(admin.ModelAdmin):
    list_display = ['rf', 'nome', 'email', 'qtd_comissoes', 'dre']
    search_fields = ['rf', 'nome', 'email', 'dre__nome', 'dre__codigo_eol']
    readonly_fields = ['id', 'uuid', 'criado_em', 'alterado_em']
    list_filter = ('dre', 'comissoes')


@admin.register(AnoAnaliseRegularidade)
class AnoAnaliseRegularidadeAdmin(admin.ModelAdmin):
    list_display = ['ano', 'atualizacao_em_massa', 'status_atualizacao', ]
    search_fields = ['ano', ]
    readonly_fields = ['criado_em', 'alterado_em']
    list_filter = ('atualizacao_em_massa', 'status_atualizacao',)


class VerificacoesInline(admin.TabularInline):
    extra = 1
    model = VerificacaoRegularidadeAssociacao


@admin.register(AnaliseRegularidadeAssociacao)
class AnaliseRegularidadeAssociacaoAdmin(admin.ModelAdmin):
    list_display = ['associacao', 'ano_analise', 'status_regularidade']
    search_fields = ['ano_analise__ano', 'associacao__nome', 'associacao__unidade__codigo_eol']
    readonly_fields = ['criado_em', 'alterado_em', 'id', 'uuid']
    list_filter = ['ano_analise', 'associacao', 'associacao__unidade__dre']
    autocomplete_fields = ['associacao', ]
    inlines = [VerificacoesInline, ]


@admin.register(VerificacaoRegularidadeAssociacao)
class VerificacaoRegularidadeAssociacaoAdmin(admin.ModelAdmin):
    list_display = ('analise_regularidade', 'item_verificacao', 'regular',)
    search_fields = (
        'uuid',
        'item_verificacao__descricao',
        'analise_regularidade__associacao__nome',
        'analise_regularidade__associacao__codigo_eol'
    )
    list_filter = (
        'analise_regularidade__ano_analise',
        'analise_regularidade__associacao__nome',
        'item_verificacao__lista',
        'item_verificacao__lista__grupo',
        'item_verificacao__descricao'
    )
    readonly_fields = ['criado_em', 'alterado_em', 'id', 'uuid']


@admin.register(AtaParecerTecnico)
class AtaParecerTecnicoAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'periodo', 'dre', 'consolidado_dre', 'sequencia_de_publicacao')
    list_filter = ['periodo', 'dre', 'consolidado_dre']
    readonly_fields = ('uuid', 'id')

    actions = ('vincular_consolidado_dre',)

    def vincular_consolidado_dre(self, request, queryset):
        from sme_ptrf_apps.dre.services.vincular_consolidado_service import VincularConsolidadoService

        for ata in queryset.all():
            VincularConsolidadoService.vincular_artefato(ata)

        self.message_user(request, f"Atas vinculadas com sucesso!")


@admin.register(PresenteAtaDre)
class PresentesAtaDreAdmin(admin.ModelAdmin):
    list_display = ('rf', 'nome', 'cargo', 'ata')
    list_filter = ['ata__dre', 'ata__periodo']
    search_fields = ['rf', 'nome', 'ata__dre__nome']
    raw_id_fields = ['ata']
    readonly_fields = ('uuid', 'id')


@admin.register(DocumentoAdicional)
class DocumentoAdicionalAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    readonly_fields = ('uuid', 'criado_em', 'alterado_em',)


@admin.register(ComentarioAnaliseConsolidadoDRE)
class ComentarioAnalisePrestacaoAdmin(admin.ModelAdmin):

    def get_dre(self, obj):
        return obj.consolidado_dre.dre if obj and obj.consolidado_dre and obj.consolidado_dre.dre else ''

    get_dre.short_description = 'DRE'

    def get_periodo(self, obj):
        return obj.consolidado_dre.periodo if obj and obj.consolidado_dre and obj.consolidado_dre.periodo else ''

    get_periodo.short_description = 'Período'

    list_display = ('get_dre', 'get_periodo', 'consolidado_dre', 'ordem', 'comentario', 'notificado_em')
    list_filter = ('consolidado_dre__dre', 'consolidado_dre__periodo', 'consolidado_dre',)
    readonly_fields = ('uuid', 'id')


@admin.register(AnaliseConsolidadoDre)
class AnaliseConsolidadoDreAdmin(admin.ModelAdmin):

    def get_dre(self, obj):
        return obj.consolidado_dre.dre if obj and obj.consolidado_dre and obj.consolidado_dre.dre else ''

    get_dre.short_description = 'DRE'

    def get_periodo(self, obj):
        return obj.consolidado_dre.periodo if obj and obj.consolidado_dre and obj.consolidado_dre.periodo else ''

    def get_id(self, obj):
        return f"Análise #{obj.pk}"

    get_id.short_description = 'Análise'

    get_periodo.short_description = 'Período'

    list_display = ('get_dre', 'get_periodo', 'consolidado_dre', 'get_id')
    list_filter = ('consolidado_dre__dre', 'consolidado_dre__periodo', 'consolidado_dre',)
    readonly_fields = ('uuid', 'id')


@admin.register(AnaliseDocumentoConsolidadoDre)
class AnaliseDocumentoConsolidadoDreAdmin(admin.ModelAdmin):

    def get_dre(self, obj):
        return obj.analise_consolidado_dre.consolidado_dre.dre if obj and obj.analise_consolidado_dre.consolidado_dre and obj.analise_consolidado_dre.consolidado_dre.dre else ''

    get_dre.short_description = 'DRE'

    def get_periodo(self, obj):
        return obj.analise_consolidado_dre.consolidado_dre.periodo if obj and obj.analise_consolidado_dre and obj.analise_consolidado_dre.consolidado_dre.periodo else ''

    get_periodo.short_description = 'Período'

    def get_analise_consolidado_dre(self, obj):
        return f'Análise Consolidado Dre #{obj.analise_consolidado_dre.pk}' if obj and obj.analise_consolidado_dre else ''

    get_analise_consolidado_dre.short_description = "Análise Consolidado"

    list_display = ('get_dre', 'get_periodo', 'get_analise_consolidado_dre', 'resultado')
    list_filter = (
        'analise_consolidado_dre__consolidado_dre__dre',
        'analise_consolidado_dre__consolidado_dre__periodo',
        'analise_consolidado_dre__consolidado_dre',
        'analise_consolidado_dre',
        'resultado',
    )
    readonly_fields = ('uuid', 'id')
