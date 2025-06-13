from django.contrib import admin
from sme_ptrf_apps.situacao_patrimonial.models import (
    BemProduzido,
    BemProduzidoDespesa,
    BemProduzidoRateio,
    BemProduzidoItem
)


class BemProduzidoRateioInline(admin.TabularInline):
    extra = 0
    model = BemProduzidoRateio
    raw_id_fields = ('rateio',)


@admin.register(BemProduzido)
class BemProduzidoAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'status',
    ]

    raw_id_fields = (
        'associacao',
    )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__nome')


@admin.register(BemProduzidoDespesa)
class BemProduzidoDespesaAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'id',
        'despesa',
    ]

    raw_id_fields = (
        'despesa',
        'bem_produzido'
    )

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    inlines = [BemProduzidoRateioInline, ]

@admin.register(BemProduzidoRateio)
class BemProduzidoRateioAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'id',
        'rateio',
    ]

    raw_id_fields = (
        'rateio',
        'bem_produzido_despesa'
    )

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

@admin.register(BemProduzidoItem)
class BemProduzidoItemAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        'bem_produzido',
        'especificacao_do_bem',
        'num_processo_incorporacao',
        'quantidade',
        'valor_individual',
    ]

    raw_id_fields = (
        'bem_produzido',
        'especificacao_do_bem'
    )

    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')