from django.contrib import admin
from sme_ptrf_apps.core.models import Recurso


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


class DespesaFilter(RecursoListFilter):
    pass


class RateioDespesaFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(despesa__recurso_id=self.value()).distinct()
        return queryset
