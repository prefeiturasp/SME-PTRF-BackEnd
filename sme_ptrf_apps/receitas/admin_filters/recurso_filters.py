from django.contrib import admin
from sme_ptrf_apps.core.models import Recurso
from django.db.models import Q


class RecursoListFilter(admin.SimpleListFilter):
    title = 'Recurso'
    parameter_name = 'recurso'

    def lookups(self, request, model_admin):
        recursos = Recurso.objects.filter(ativo=True).order_by('nome')
        return [(str(r.id), r.nome) for r in recursos]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(associacao__periodos_iniciais__recurso_id=self.value()).distinct()
        return queryset


class DetalheTipoReceitaFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(receita__associacao__periodos_iniciais__recurso_id=self.value()).distinct()
        return queryset


class ReceitaFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(acao_associacao__acao__recurso=self.value()) |
                Q(conta_associacao__tipo_conta__recurso=self.value())
            ).distinct()

        return queryset


class RepasseFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo__recurso_id=self.value()).distinct()
        return queryset
