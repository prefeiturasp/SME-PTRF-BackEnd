from django.contrib import admin
from sme_ptrf_apps.situacao_patrimonial.models import (
    BemProduzido,
    BemProduzidoDespesa,
    BemProduzidoRateio
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
        'especificacao_do_bem',
        'num_processo_incorporacao',
        'quantidade',
        'valor_individual',
    ]

    raw_id_fields = (
        'especificacao_do_bem',
        'associacao'
    )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    search_fields = ('associacao__unidade__codigo_eol', 'associacao__nome', 'associacao__unidade__nome',
                     'especificacao_do_bem__descricao', 'num_processo_incorporacao')


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
