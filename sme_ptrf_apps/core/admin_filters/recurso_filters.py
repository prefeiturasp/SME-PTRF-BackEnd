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


class RecursoAssociacaoListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodos_iniciais__recurso_id=self.value()).distinct()
        return queryset


class DemonstrativoFinanceiroListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prestacao_conta__periodo__recurso_id=self.value()).distinct()
        return queryset


class RelacaoBensListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prestacao_conta__periodo__recurso_id=self.value()).distinct()
        return queryset


class DevolucaoPrestacaoContaFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prestacao_conta__periodo__recurso_id=self.value()).distinct()
        return queryset


class AnalisePrestacaoContaFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prestacao_conta__periodo__recurso_id=self.value()).distinct()
        return queryset


class RecursoContasAssociacaoListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tipo_conta__recurso_id=self.value()).distinct()
        return queryset


class AcaoAssociacaoAListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(acao__recurso_id=self.value()).distinct()
        return queryset


class PrestacaoContaListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo__recurso_id=self.value()).distinct()
        return queryset

        
class PeriodoRecursoListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo__recurso_id=self.value()).distinct()
        return queryset

class AtaListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo__recurso_id=self.value()).distinct()
        return queryset


class ObservacaoConciliacaoFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(periodo__recurso_id=self.value()).distinct()
        return queryset


class AnaliseConsolidadoDreListFilter(RecursoListFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(consolidado_dre__periodo__recurso_id=self.value()).distinct()
        return queryset
