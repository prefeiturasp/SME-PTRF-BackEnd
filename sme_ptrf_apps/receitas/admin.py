from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from sme_ptrf_apps.receitas.models import Receita, TipoReceita, Repasse, DetalheTipoReceita


@admin.register(TipoReceita)
class TipoReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'e_repasse', 'e_rendimento', 'aceita_capital', 'aceita_custeio', 'aceita_livre')


def customTitledFilter(title):
   class Wrapper(admin.FieldListFilter):
       def __new__(cls, *args, **kwargs):
           instance = admin.FieldListFilter.create(*args, **kwargs)
           instance.title = title
           return instance
   return Wrapper


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):

    list_display = ('data', 'valor', 'categoria_receita', 'detalhamento', 'associacao', 'repasse',)
    ordering = ('-data',)
    search_fields = ('detalhe_tipo_receita__nome', 'detalhe_outros')
    list_filter = (
        ('data', DateRangeFilter),
        ('associacao__nome', customTitledFilter('Associação')),
        ('associacao__unidade__dre', customTitledFilter('DRE')),
        ('acao_associacao__acao__nome', customTitledFilter('Ação')),
        ('conta_associacao__tipo_conta__nome', customTitledFilter('Tipo Conta')),
        ('tipo_receita', customTitledFilter('Tipo Receita')),
        'detalhe_tipo_receita',
        'categoria_receita',
        'repasse',
    )
    readonly_fields = ('uuid', 'id')


@admin.register(Repasse)
class RepasseAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'valor_capital', 'valor_custeio', 'valor_livre', 'tipo_conta', 'acao', 'status')

    def tipo_conta(self, obj):
        return obj.conta_associacao.tipo_conta

    def acao(self, obj):
        return obj.acao_associacao.acao.nome


@admin.register(DetalheTipoReceita)
class DetalheTipoReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_receita')
    readonly_fields = ('uuid', 'id')
    search_fields = ('nome',)
    list_filter = ('tipo_receita',)
