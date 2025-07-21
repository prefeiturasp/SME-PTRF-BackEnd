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

    search_help_text = 'Pesquise por: código eol da associação, nome da associação, nome da unidade'


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

    search_fields = ('despesa__associacao__unidade__codigo_eol', 'despesa__associacao__nome',
                     'despesa__associacao__unidade__nome', 'despesa__uuid')

    inlines = [BemProduzidoRateioInline, ]

    search_help_text = 'Pesquise por: uuid da despesa, código eol da associação, nome da associação, nome da unidade'


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

    search_fields = ('rateio__uuid', 'rateio__despesa__associacao__unidade__codigo_eol', 'rateio__despesa__associacao__nome',
                     'rateio__despesa__associacao__unidade__nome', 'rateio__despesa__uuid')

    search_help_text = 'Pesquise por: uuid do rateio, uuid da despesa, código eol da associação, nome da associação, nome da unidade'


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

    search_fields = ('bem_produzido__uuid', 'bem_produzido__associacao__unidade__codigo_eol', 'bem_produzido__associacao__nome',
                     'bem_produzido__associacao__unidade__nome')

    search_help_text = 'Pesquise por: uuid do bem produzido, código eol da associação, nome da associação, nome da unidade'
