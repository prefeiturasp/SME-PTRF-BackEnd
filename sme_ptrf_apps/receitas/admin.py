from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from sme_ptrf_apps.receitas.models import Receita, TipoReceita, Repasse, DetalheTipoReceita, MotivoEstorno


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
    raw_id_fields = (
        'associacao',
        'conta_associacao',
        'acao_associacao',
        'tipo_receita',
        'repasse',
        'detalhe_tipo_receita',
        'referencia_devolucao',
        'periodo_conciliacao',
        'saida_do_recurso',
        'rateio_estornado',
    )
    list_display = ('data', 'valor', 'categoria_receita', 'detalhamento', 'associacao', 'repasse','status')
    ordering = ('-data',)
    search_fields = (
        'detalhe_tipo_receita__nome',
        'detalhe_outros',
        'associacao__nome',
        'associacao__unidade__nome',
        'associacao__unidade__codigo_eol'
    )
    list_filter = (
        ('conferido', customTitledFilter('Conferido')),
        ('data', DateRangeFilter),
        ('associacao__unidade__dre', customTitledFilter('DRE')),
        ('acao_associacao__acao__nome', customTitledFilter('Ação')),
        ('conta_associacao__tipo_conta__nome', customTitledFilter('Tipo Conta')),
        ('tipo_receita', customTitledFilter('Tipo Receita')),
        'categoria_receita',
        'status',
    )
    readonly_fields = ('uuid', 'id',)
    actions = ['conciliar_receita', 'desconciliar_receita', ]

    def conciliar_receita(self, request, queryset):
        for receita in queryset.all():
            receita.marcar_conferido()

        self.message_user(request, f"Processo Terminado. Verifique o status do processo.")

    conciliar_receita.short_description = "Conciliar receitas."

    def desconciliar_receita(self, request, queryset):
        for receita in queryset.all():
            receita.desmarcar_conferido()

        self.message_user(request, f"Processo Terminado. Verifique o status do processo.")

    desconciliar_receita.short_description = "Desconciliar receitas."


@admin.register(Repasse)
class RepasseAdmin(admin.ModelAdmin):
    search_fields = ('associacao__nome', 'associacao__unidade__codigo_eol', 'carga_origem_linha_id')
    list_display = ('associacao', 'periodo', 'valor_capital', 'valor_custeio', 'valor_livre', 'tipo_conta', 'acao', 'status')
    list_filter = ('periodo', 'status', 'carga_origem')
    # Campos tipo autocomplete substituem o componente padrão de seleção de chaves extrangeiras e são bem mais rápidos.
    autocomplete_fields = ['associacao', 'periodo', 'conta_associacao', 'acao_associacao', 'carga_origem']

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


@admin.register(MotivoEstorno)
class MotivoEstornoAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'uuid', )
    readonly_fields = ('uuid', 'id')
    search_fields = ('motivo', )
