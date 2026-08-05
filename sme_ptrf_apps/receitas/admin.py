from django.contrib import admin, messages
from django.forms import ModelForm, ModelChoiceField
from django.core.exceptions import ValidationError
from rangefilter.filters import DateRangeFilter
from rest_framework import request
from sme_ptrf_apps.core.models import Unidade, Recurso
from sme_ptrf_apps.receitas.models import Receita, TipoReceita, Repasse, DetalheTipoReceita, MotivoEstorno

from .admin_filters import (
    ReceitaFilter,
    RepasseFilter,
    DetalheTipoReceitaFilter
)

class DetalheTipoReceitaInline(admin.TabularInline):
    model = DetalheTipoReceita
    extra = 0
    Fields = ['nome',]

class TipoReceitaForm(ModelForm):
    def clean_unidades(self):
        unidades = self.cleaned_data['unidades']

        if unidades.exists():
            unidades_com_receita_do_tipo = Receita.objects.filter(tipo_receita=self.instance).distinct(
                'associacao').values_list('associacao__unidade', flat=True)
            unidades_selecionadas = unidades.values_list('codigo_eol', flat=True)

            if len(unidades_com_receita_do_tipo) > 0 and not (unidades.filter(codigo_eol__in=unidades_com_receita_do_tipo).exists() and (len(unidades_selecionadas) == len(unidades_com_receita_do_tipo))):  # noqa
                unidades_faltantes = Unidade.objects.filter(codigo_eol__in=unidades_com_receita_do_tipo).exclude(
                    codigo_eol__in=unidades_selecionadas).values_list('codigo_eol', flat=True)
                if len(unidades_faltantes) > 0:
                    raise ValidationError(
                        ("Não é possível restringir tipo de receita, pois existem unidades que"
                         " já possuem receita criada com esse tipo e não estão selecionadas."
                         f" Unidades faltantes: {list(unidades_faltantes)}"))
        return unidades


class RecursoFilter(admin.SimpleListFilter):
    title = 'Recurso'
    parameter_name = 'recurso'

    def lookups(self, request, model_admin):
        from sme_ptrf_apps.core.models import Recurso
        recursos = Recurso.objects.all()
        return [(recurso.uuid, recurso.nome) for recurso in recursos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(recurso__uuid=self.value())
        return queryset


@admin.register(TipoReceita)
class TipoReceitaAdmin(admin.ModelAdmin):
    form = TipoReceitaForm
    inlines = [DetalheTipoReceitaInline]
    list_display = (
        'nome', 'recurso', 'e_repasse', 'e_rendimento', 'aceita_capital', 'aceita_custeio', 'aceita_livre',
        'mensagem_usuario', 'possui_detalhamento'
    )
    readonly_fields = ('uuid',)
    autocomplete_fields = ('unidades',)
    list_filter = (
        RecursoFilter,
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
    list_display = ('data', 'valor', 'categoria_receita', 'detalhamento', 'associacao', 'repasse', 'status')
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
        ReceitaFilter
    )
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    actions = ['conciliar_receita', 'desconciliar_receita', ]

    def conciliar_receita(self, request, queryset):
        for receita in queryset.all():
            receita.marcar_conferido()

        self.message_user(request, "Processo Terminado. Verifique o status do processo.")

    conciliar_receita.short_description = "Conciliar receitas."

    def desconciliar_receita(self, request, queryset):
        for receita in queryset.all():
            receita.desmarcar_conferido()

        self.message_user(request, "Processo Terminado. Verifique o status do processo.")

    desconciliar_receita.short_description = "Desconciliar receitas."


@admin.register(Repasse)
class RepasseAdmin(admin.ModelAdmin):
    search_fields = ('associacao__nome', 'associacao__unidade__codigo_eol', 'carga_origem_linha_id')
    list_display = ('associacao', 'periodo', 'valor_capital', 'valor_custeio',
                    'valor_livre', 'tipo_conta', 'acao', 'status')
    list_filter = ('periodo', 'status', 'carga_origem', 'associacao__unidade__dre', RepasseFilter,)
    raw_id_fields = ('associacao', 'periodo', 'conta_associacao', 'acao_associacao', 'carga_origem')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')

    def tipo_conta(self, obj):
        return obj.conta_associacao.tipo_conta if obj.conta_associacao else ''

    def acao(self, obj):
        return obj.acao_associacao.acao.nome if obj.acao_associacao else ''

    def get_queryset(self, request):
        return super(RepasseAdmin, self).get_queryset(request).select_related(
            'conta_associacao', 'acao_associacao', 'periodo', 'associacao')


@admin.register(DetalheTipoReceita)
class DetalheTipoReceitaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_receita', 'recurso')
    readonly_fields = ('uuid', 'id')
    search_fields = ('nome',)
    list_filter = ('tipo_receita', DetalheTipoReceitaFilter)

    @admin.display(description='Recurso', ordering='tipo_receita__recurso__nome')
    def recurso(self, obj):
        return obj.tipo_receita.recurso if obj.tipo_receita else None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tipo_receita__recurso')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk and obj.receitas.exists():
            return self.readonly_fields + ('tipo_receita',)
        return self.readonly_fields

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'GET':
            obj = self.get_object(request, object_id)
            if obj and obj.receitas.exists():
                message = "Não é possível alterar o Tipo de Receita, pois existem receitas associadas a este detalhe."
                messages.warning(request, message)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, **kwargs):
        _request = request

        class DetalheTipoReceitaForm(ModelForm):
            recurso = ModelChoiceField(
                queryset=Recurso.objects.filter(ativo=True).order_by('nome'),
                required=False,
                label='Recurso',
                empty_label='--- Selecione um recurso ---',
            )

            def __init__(self, *args, **form_kwargs):
                super().__init__(*args, **form_kwargs)

                can_write_tipo_receita = self.fields.get('tipo_receita', None)

                if can_write_tipo_receita and self.instance and self.instance.pk and self.instance.receitas.exists():
                    self.fields['tipo_receita'].disabled = True

                recurso_id = _request.GET.get('recurso')

                if not recurso_id and self.instance and self.instance.pk and self.instance.tipo_receita.recurso:
                    if self.instance.tipo_receita.recurso_id:
                        recurso_id = self.instance.tipo_receita.recurso_id

                if recurso_id:
                    try:
                        self.fields['recurso'].initial = Recurso.objects.get(pk=recurso_id)
                    except Recurso.DoesNotExist:
                        pass
                    if can_write_tipo_receita:
                        self.fields['tipo_receita'].queryset = TipoReceita.objects.filter(
                            recurso_id=recurso_id, possui_detalhamento=True
                        ).distinct().order_by('nome')
                elif can_write_tipo_receita:
                    self.fields['tipo_receita'].queryset = TipoReceita.objects.filter(possui_detalhamento=True).order_by('nome')

            class Meta:
                model = DetalheTipoReceita
                fields = ('recurso', 'nome', 'tipo_receita')

            def clean(self):
                cleaned_data = super().clean()
                nome = cleaned_data.get("nome")
                tipo_receita = cleaned_data.get("tipo_receita")

                if not tipo_receita:
                    raise ValidationError("O campo Tipo de Receita é obrigatório.")

                # Normaliza o nome: remove espaços em branco extras
                if nome:
                    nome = ' '.join(nome.split())
                    cleaned_data['nome'] = nome

                if DetalheTipoReceita.objects.filter(nome__iexact=nome, tipo_receita=tipo_receita).exists():
                    raise ValidationError("Este detalhe já existe para esse tipo de receita.")

                if tipo_receita and not tipo_receita.possui_detalhamento:
                    raise ValidationError("Não é possível associar um detalhe a um tipo de receita que não permite detalhamento.")

                if self.instance and self.instance.pk:
                    if tipo_receita and tipo_receita != self.instance.tipo_receita:
                        if self.instance.receitas.exists():
                            raise ValidationError(
                                "Não é possível alterar o Tipo de Receita, pois existem receitas associadas a este detalhe."
                            )

            class Media:
                js = ('admin/js/detalhe_tipo_receita.js',)

        kwargs['form'] = DetalheTipoReceitaForm
        return super().get_form(request, obj, **kwargs)


@admin.register(MotivoEstorno)
class MotivoEstornoAdmin(admin.ModelAdmin):
    list_display = ('motivo', 'uuid', 'recurso')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('motivo', )
    list_filter = (RecursoFilter,)


