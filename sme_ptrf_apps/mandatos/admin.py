from django.contrib import admin

from .models import Mandato, Composicao, CargoComposicao, OcupanteCargo


@admin.register(Mandato)
class MandatoAdmin(admin.ModelAdmin):
    list_display = ('referencia_mandato', 'data_inicial', 'data_final')


@admin.register(Composicao)
class ComposicaoAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'mandato', 'data_inicial', 'data_final')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('mandato', 'associacao')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('associacao',)


@admin.register(CargoComposicao)
class CargoComposicaoAdmin(admin.ModelAdmin):
    list_display = ('composicao', 'ocupante_do_cargo', 'cargo_associacao', 'substituto', 'substituido')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('composicao__associacao__unidade__codigo_eol', 'composicao__associacao__unidade__nome')
    list_filter = ('composicao', 'composicao__associacao')


@admin.register(OcupanteCargo)
class OcupanteCargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'representacao', 'cargo_educacao')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
