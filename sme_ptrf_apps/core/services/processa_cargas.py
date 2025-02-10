from sme_ptrf_apps.core.choices.tipos_carga import (CARGA_PERIODO_INICIAL, CARGA_REPASSE_REALIZADO,
                                                    CARGA_REPASSE_PREVISTO, CARGA_ACOES_ASSOCIACOES,
                                                    CARGA_ASSOCIACOES, CARGA_USUARIOS, CARGA_CENSO,
                                                    CARGA_REPASSE_PREVISTO_SME, CARGA_DEVOLUCAO_TESOURO,
                                                    CARGA_MATERIAIS_SERVICOS
                                                    )
from sme_ptrf_apps.core.services.periodo_inicial import carrega_periodo_inicial
from sme_ptrf_apps.core.services.carga_censo import carrega_censo
from sme_ptrf_apps.core.services.carga_previsao_repasse import carrega_previsoes_repasses
from sme_ptrf_apps.core.services.carga_associacoes_service import CargaAssociacoesService
from sme_ptrf_apps.core.services.carga_acoes_associacoes_service import CargaAcoesAssociacoesService
from sme_ptrf_apps.core.services.carga_devolucoes_tesouro_service import CargaDevolucoesTesouroService
from sme_ptrf_apps.receitas.services.carga_repasses_previstos import carrega_repasses_previstos
from sme_ptrf_apps.receitas.services.carga_repasses_realizados import carrega_repasses_realizados
from sme_ptrf_apps.users.services.carga_usuario_service import CargaUsuariosService
from sme_ptrf_apps.users.services.carga_usuario_v2_service import CargaUsuariosGestaoUsuarioService
from sme_ptrf_apps.despesas.services.carga_materiais_servicos_service import CargaMateriaisServicosService
from waffle import get_waffle_flag_model

def processa_cargas(queryset):
    for arquivo in queryset.all():
        processa_carga(arquivo)


def processa_carga(arquivo):
    arquivo.inicia_processamento()

    if arquivo.tipo_carga == CARGA_REPASSE_REALIZADO:
        carrega_repasses_realizados(arquivo)
    elif arquivo.tipo_carga == CARGA_PERIODO_INICIAL:
        carrega_periodo_inicial(arquivo)
    elif arquivo.tipo_carga == CARGA_REPASSE_PREVISTO:
        carrega_repasses_previstos(arquivo)
    elif arquivo.tipo_carga == CARGA_ASSOCIACOES:
        CargaAssociacoesService().carrega_associacoes(arquivo)
    elif arquivo.tipo_carga == CARGA_ACOES_ASSOCIACOES:
        CargaAcoesAssociacoesService().carrega_acoes_associacoes(arquivo)
    elif arquivo.tipo_carga == CARGA_USUARIOS:
        flags = get_waffle_flag_model()

        if flags.objects.filter(name='gestao-usuarios', everyone=True).exists():
            CargaUsuariosGestaoUsuarioService().carrega_usuarios(arquivo)
        else:
            CargaUsuariosService().carrega_usuarios(arquivo)

    elif arquivo.tipo_carga == CARGA_CENSO:
        carrega_censo(arquivo)
    elif arquivo.tipo_carga == CARGA_REPASSE_PREVISTO_SME:
        carrega_previsoes_repasses(arquivo)
    elif arquivo.tipo_carga == CARGA_DEVOLUCAO_TESOURO:
        CargaDevolucoesTesouroService().carrega_devolucoes_tesouro(arquivo)
    elif arquivo.tipo_carga == CARGA_MATERIAIS_SERVICOS:
        CargaMateriaisServicosService().carrega_materiais_servicos(arquivo)
