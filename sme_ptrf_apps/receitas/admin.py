from django.contrib import admin

from sme_ptrf_apps.receitas.models import Receita, TipoReceita, Repasse

from rangefilter.filter import DateRangeFilter

admin.site.register(TipoReceita)


def customTitledFilter(title):
   class Wrapper(admin.FieldListFilter):
       def __new__(cls, *args, **kwargs):
           instance = admin.FieldListFilter.create(*args, **kwargs)
           instance.title = title
           return instance
   return Wrapper


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('data', 'valor', 'descricao', 'associacao',)
    ordering = ('-data',)
    search_fields = ('descricao',)
    list_filter = (
        ('data', DateRangeFilter),
        ('associacao__nome', customTitledFilter('Associação')), 
        ('acao_associacao__acao__nome', customTitledFilter('Ação')), 
        ('conta_associacao__tipo_conta__nome', customTitledFilter('Tipo Conta')),
        ('tipo_receita', customTitledFilter('Tipo Receita')))
    readonly_fields = ('uuid', 'id')


@admin.register(Repasse)
class RepasseAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'valor_capital', 'valor_custeio', 'tipo_conta', 'acao')
    actions = ['importa_repasses',]

    def tipo_conta(self, obj):
        return obj.conta_associacao.tipo_conta

    def acao(self, obj):
        return obj.acao_associacao.acao.nome

    def importa_repasses(self, request, queryset):
        from sme_ptrf_apps.receitas.services.carga_repasses import carrega_repasses
        carrega_repasses()
        self.message_user(request, "Repasses Carregados")

    importa_repasses.short_description = "Fazer carga de repasses."
