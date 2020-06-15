from sme_ptrf_apps.core.models.arquivo import CARGA_REPASSE_REALIZADO
from sme_ptrf_apps.receitas.services.carga_repasses_realizados import carrega_repasses


def processa_cargas(queryset):
    for arquivo in queryset.all():
        if arquivo.tipo_carga == CARGA_REPASSE_REALIZADO:
            carrega_repasses(arquivo)
