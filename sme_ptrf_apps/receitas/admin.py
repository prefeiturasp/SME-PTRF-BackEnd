from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from sme_ptrf_apps.receitas.models import Receita, TipoReceita, Repasse, DetalheTipoReceita


@admin.register(TipoReceita)
class TipoReceitaAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'e_repasse', 'e_rendimento', 'aceita_capital', 'aceita_custeio', 'aceita_livre',
        'mensagem_usuario', 'possui_detalhamento'
    )


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
    readonly_fields = ('uuid', 'id',)


@admin.register(Repasse)
class RepasseAdmin(admin.ModelAdmin):
    search_fields = ('associacao__nome', 'associacao__unidade__codigo_eol')
    list_display = ('associacao', 'periodo', 'valor_capital', 'valor_custeio', 'valor_livre', 'tipo_conta', 'acao', 'status')
    list_filter = ('periodo', 'status')
    # Campos tipo autocomplete substituem o componente padrão de seleção de chaves extrangeiras e são bem mais rápidos.
    autocomplete_fields = ['associacao', 'periodo', 'conta_associacao', 'acao_associacao']

    def tipo_conta(self, obj):
        return obj.conta_associacao.tipo_conta if obj.conta_associacao else ''

    def acao(self, obj):
        return obj.acao_associacao.acao.nome if obj.acao_associacao else ''

    def get_queryset(self, request):
        return super(RepasseAdmin, self).get_queryset(request).select_related(
            'conta_associacao', 'acao_associacao', 'periodo', 'associacao')


@admin.register(DetalheTipoReceita)
class DetalheTipoReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_receita')
    readonly_fields = ('uuid', 'id')
    search_fields = ('nome',)
    list_filter = ('tipo_receita',)
