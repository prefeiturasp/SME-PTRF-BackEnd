from sme_ptrf_apps.core.models.arquivo import (CARGA_PERIODO_INICIAL, CARGA_REPASSE_REALIZADO, CARGA_REPASSE_PREVISTO,
                                               CARGA_ASSOCIACOES, CARGA_USUARIOS, CARGA_CENSO, CARGA_REPASSE_PREVISTO_SME)
from sme_ptrf_apps.core.services.carga_associacoes import carrega_associacoes
from sme_ptrf_apps.core.services.periodo_inicial import carrega_periodo_inicial
from sme_ptrf_apps.core.services.carga_censo import carrega_censo
from sme_ptrf_apps.core.services.carga_previsao_repasse import carrega_previsoes_repasses
from sme_ptrf_apps.receitas.services.carga_repasses_previstos import carrega_repasses_previstos
from sme_ptrf_apps.receitas.services.carga_repasses_realizados import carrega_repasses_realizados
from sme_ptrf_apps.users.services.carga_usuarios import carrega_usuarios

def processa_cargas(queryset):
    for arquivo in queryset.all():
        if arquivo.tipo_carga == CARGA_REPASSE_REALIZADO:
            carrega_repasses_realizados(arquivo)
        elif arquivo.tipo_carga == CARGA_PERIODO_INICIAL:
            carrega_periodo_inicial(arquivo)
        elif arquivo.tipo_carga == CARGA_REPASSE_PREVISTO:
            carrega_repasses_previstos(arquivo)
        elif arquivo.tipo_carga == CARGA_ASSOCIACOES:
            carrega_associacoes(arquivo)
        elif arquivo.tipo_carga == CARGA_USUARIOS:
            carrega_usuarios(arquivo)
        elif arquivo.tipo_carga == CARGA_CENSO:
            carrega_censo(arquivo)
        elif arquivo.tipo_carga == CARGA_REPASSE_PREVISTO_SME:
            carrega_previsoes_repasses(arquivo)
