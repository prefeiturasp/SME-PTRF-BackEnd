from django.contrib import admin
from sme_ptrf_apps.paa.models import (
    Paa,
    ReceitaPrevistaPaa,
    RecursoProprioPaa,
    ReceitaPrevistaPdde,
    PrioridadePaa,
    AtaPaa,
    DocumentoPaa,
    ReceitaPrevistaOutroRecursoPeriodo
)


class ObjetivosPaaInline(admin.TabularInline):
    model = Paa.objetivos.through
    extra = 0
    fields = (
        'get_uuid',
        'get_nome',
        'get_status',
        'get_objetivo_do_paa',
    )
    readonly_fields = fields
    can_delete = False
    verbose_name = 'Objetivo'
    verbose_name_plural = 'Objetivos'

    def has_add_permission(self, request, obj=None):
        return False

    def get_uuid(self, obj):
        return obj.objetivopaa.uuid
    get_uuid.short_description = 'UUID'

    def get_nome(self, obj):
        return obj.objetivopaa.nome
    get_nome.short_description = 'Nome'

    def get_status(self, obj):
        return obj.objetivopaa.get_status_display()
    get_status.short_description = 'Status'

    def get_objetivo_do_paa(self, obj):
        return obj.objetivopaa.paa_id is not None
    get_objetivo_do_paa.short_description = 'Criado no PAA'
    get_objetivo_do_paa.boolean = True


class AtividadeEstatutariaPaaInline(admin.TabularInline):
    model = Paa.atividades_estatutarias.through
    extra = 0
    fields = (
        'uuid',
        'atividade_estatutaria',
        'data',
        'get_atividade_estatutaria_do_paa',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def get_atividade_estatutaria_do_paa(self, obj):
        return obj.atividade_estatutaria.paa_id is not None
    get_atividade_estatutaria_do_paa.short_description = 'Criada no PAA'
    get_atividade_estatutaria_do_paa.boolean = True


class ReceitasPrevistasPTRFInline(admin.TabularInline):
    model = ReceitaPrevistaPaa
    extra = 0
    fields = (
        'uuid',
        'acao_associacao',
        'saldo_congelado_custeio',
        'saldo_congelado_capital',
        'saldo_congelado_livre',
        'previsao_valor_custeio',
        'previsao_valor_capital',
        'previsao_valor_livre',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class ReceitasPrevistasPDDEInline(admin.TabularInline):
    model = ReceitaPrevistaPdde
    extra = 0
    fields = (
        'uuid',
        'acao_pdde',
        'saldo_custeio',
        'saldo_capital',
        'saldo_livre',
        'previsao_valor_custeio',
        'previsao_valor_capital',
        'previsao_valor_livre',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class ReceitasPrevistasRecursoProprioInline(admin.TabularInline):
    model = RecursoProprioPaa
    extra = 0
    fields = (
        'uuid',
        'fonte_recurso',
        'associacao',
        'data_prevista',
        'descricao',
        'valor',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class ReceitasPrevistasOutrosRecursosPeriodoInline(admin.TabularInline):
    model = ReceitaPrevistaOutroRecursoPeriodo
    extra = 0
    fields = (
        'uuid',
        'outro_recurso_periodo',
        'saldo_custeio',
        'saldo_capital',
        'saldo_livre',
        'previsao_valor_custeio',
        'previsao_valor_capital',
        'previsao_valor_livre',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class PrioridadesPaaInline(admin.TabularInline):
    model = PrioridadePaa
    extra = 0
    fk_name = 'paa'
    fields = (
        'uuid',
        'prioridade',
        'recurso',
        'tipo_aplicacao',
        'valor_total',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class DocumentoPAAInline(admin.TabularInline):
    model = DocumentoPaa
    extra = 0
    fields = (
        'arquivo_pdf',
        'status_geracao',
        'versao',
        'versao_documento',
        'retificacao',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class AtaPAAInline(admin.TabularInline):
    model = AtaPaa
    extra = 0
    fields = (
        'arquivo_pdf',
        'tipo_ata',
        'status_geracao_pdf',
        'parecer_conselho',
        'preenchida_em',
        'previa',
        'justificativa',
        'pdf_gerado_previamente',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False
