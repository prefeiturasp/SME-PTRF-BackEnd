from django.contrib import admin
from sme_ptrf_apps.paa.models import (
    ReceitaPrevistaPaa,
    RecursoProprioPaa,
    ReceitaPrevistaPdde,
    PrioridadePaa,
    ObjetivoPaa,
    AtaPaa,
    AtividadeEstatutariaPaa,
    DocumentoPaa,
    ReceitaPrevistaOutroRecursoPeriodo
)


class ObjetivosPaaInline(admin.TabularInline):
    model = ObjetivoPaa
    extra = 0
    fields = (
        'uuid',
        'nome',
        'status',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class AtividadeEstatutariaPaaInline(admin.TabularInline):
    model = AtividadeEstatutariaPaa
    extra = 0
    fields = (
        'uuid',
        'atividade_estatutaria',
        'data',
    )
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


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
        # 'acao_associacao',
        # 'programa_pdde',
        # 'acao_pdde',
        # 'outro_recurso',
        'tipo_aplicacao',
        # 'tipo_despesa_custeio',
        # 'especificacao_material',
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
