from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from waffle import flag_is_active

from .models import (
    Mandato, Composicao, CargoComposicao, OcupanteCargo, SolicitacaoDeMigracao,
    CargoComposicaoVacancia, ComposicaoVacancia
)
from .services import (
    ServicoSolicitacaoDeMigracao,
    ServicoMandatoVigente,
    ServicoMandatoVigenteVacancia,
    ServicoSolicitacaoDeMigracaoVacancia,
)


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
    list_display = ('ocupante_do_cargo', 'cargo_associacao', 'substituto', 'substituido', 'composicao')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('ocupante_do_cargo__nome', 'composicao__associacao__unidade__codigo_eol',
                     'composicao__associacao__unidade__nome')
    raw_id_fields = ('composicao', 'ocupante_do_cargo')


@admin.register(OcupanteCargo)
class OcupanteCargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'representacao', 'cargo_educacao', 'codigo_identificacao', 'cpf_responsavel')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('nome', 'representacao', 'cargo_educacao')


@admin.register(SolicitacaoDeMigracao)
class SolicitacaoDeMigracaoAdmin(admin.ModelAdmin):
    list_display = ('eol_unidade', 'dre', 'todas_as_unidades', 'status_processamento')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    list_filter = ('eol_unidade', 'dre', 'todas_as_unidades')
    list_display_links = ('eol_unidade', 'dre', 'todas_as_unidades')
    raw_id_fields = ('eol_unidade',)
    actions = ['executa_migracao', ]

    def executa_migracao(self, request, queryset):
        """Dispara a migração de membros legados para o Histórico de Membros (v1 e/ou v2).

        As duas migrações são checadas de forma independente (não são mutuamente exclusivas):
        se ambas as flags `historico-de-membros` e `historico-de-membros-v2` estiverem ativas,
        as duas migrações são disparadas para o mesmo queryset, cada uma gravando na sua própria
        estrutura de dados (`Composicao`/`CargoComposicao` para a v1, `ComposicaoVacancia`/
        `CargoComposicaoVacancia` para a v2).

        Args:
            request: requisição do Django Admin, usada para checar as feature flags.
            queryset: `SolicitacaoDeMigracao` selecionadas na lista do admin.
        """
        if flag_is_active(request, 'historico-de-membros'):
            servico_mandato_vigente = ServicoMandatoVigente()
            mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

            if not mandato_vigente:
                self.message_user(request, mark_safe("<strong>Erro: Não existe um mandato vigente cadastrado</strong>"),
                                  level=messages.ERROR)
            else:
                ServicoSolicitacaoDeMigracao().executa_migracoes(queryset)
                self.message_user(request, mark_safe(
                    "<strong>Atenção! Processo de migração iniciado. </br> "
                    "Este processo rodará em segundo plano e pode demorar! </br> "
                    "Volte mais tarde e verifique o Status do Processamento</strong>"
                ), level=messages.WARNING)

        if flag_is_active(request, 'historico-de-membros-v2'):
            srv = ServicoMandatoVigenteVacancia()
            mandato_vigente = srv.get_mandato_vigente()

            if not mandato_vigente:
                self.message_user(
                    request,
                    mark_safe("<strong>Erro: Não existe um mandato vigente cadastrado</strong>"),
                    level=messages.ERROR)
            else:
                ServicoSolicitacaoDeMigracaoVacancia().executa_migracoes(queryset)
                self.message_user(
                    request,
                    mark_safe(
                        "<strong>Atenção! Processo de migração de vacância iniciado. </br> "
                        "Este processo rodará em segundo plano e pode demorar! </br> "
                        "Volte mais tarde e verifique o Status do Processamento</strong>"
                    ),
                    level=messages.WARNING)
    executa_migracao.short_description = "Realizar migração"


@admin.register(ComposicaoVacancia)
class ComposicaoVacanciaAdmin(admin.ModelAdmin):
    list_display = ('associacao', 'mandato', 'data_inicial', 'data_final')
    search_fields = ('associacao__unidade__codigo_eol', 'associacao__unidade__nome', 'associacao__nome')
    list_filter = ('mandato', 'associacao')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    raw_id_fields = ('associacao',)

    def data_inicial(self, obj):
        return obj.mandato.data_inicial
    data_inicial.short_description = 'Início Mandato'

    def data_final(self, obj):
        return obj.mandato.data_final
    data_final.short_description = 'Término Mandato'


@admin.register(CargoComposicaoVacancia)
class CargoComposicaoVacanciaAdmin(admin.ModelAdmin):
    list_display = ('ocupante_do_cargo', 'cargo_associacao', 'data_inicio_no_cargo', 'data_fim_no_cargo', 'composicao')
    readonly_fields = ('uuid', 'id', 'criado_em', 'alterado_em')
    search_fields = ('ocupante_do_cargo__nome', 'composicao__associacao__unidade__codigo_eol',
                     'composicao__associacao__unidade__nome')
    raw_id_fields = ('composicao', 'ocupante_do_cargo', 'substituido_por')
    list_filter = ('cargo_associacao',)
