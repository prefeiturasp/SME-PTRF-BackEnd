import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    Periodo,
    Unidade,
)

from sme_ptrf_apps.dre.models import (
    ConsolidadoDRE
)

logger = logging.getLogger(__name__)


def gerar_previa_relatorio_consolidado_dre(
    dre_uuid,
    periodo_uuid,
    parcial,
    usuario,
    consolidado_dre_uuid,
    sequencia_de_publicacao,
    apenas_nao_publicadas,
):
    from sme_ptrf_apps.dre.services import _criar_previa_demonstrativo_execucao_fisico_financeiro

    logger.info(
        f'Iniciando a Prévia do Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid} ')

    try:
        periodo = Periodo.objects.get(uuid=periodo_uuid)
    except Periodo.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        dre = Unidade.dres.get(uuid=dre_uuid)
    except Unidade.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        if consolidado_dre_uuid:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        else:
            consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo,
                                                         sequencia_de_publicacao=sequencia_de_publicacao)
    except ConsolidadoDRE.DoesNotExist:
        erro = {
            'erro': 'Objeto não encontrado.',
            'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
        }
        logger.error('Erro: %r', erro)
        raise Exception(erro)

    try:
        _criar_previa_demonstrativo_execucao_fisico_financeiro(
            dre,
            periodo,
            usuario,
            consolidado_dre,
            parcial,
            apenas_nao_publicadas
        )
    except Exception as err:
        erro = {
            'erro': 'problema_geracao_previa_relatorio',
            'mensagem': 'Erro ao gerar prévia do relatório.'
        }
        logger.error("Erro ao gerar prévia relatório consolidado: %s", str(err))
        raise Exception(erro)

    logger.info(
        f'Finalizado Prévia do Relatório DRE. DRE:{dre_uuid} Período:{periodo_uuid}')


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_previa_consolidado_dre_async(
    dre_uuid=None,
    periodo_uuid=None,
    parcial=None,
    usuario=None,
    consolidado_dre_uuid=None,
    sequencia_de_publicacao=None,
    apenas_nao_publicadas=False,
):
    from ..services.consolidado_dre_service import atrelar_pc_ao_consolidado_dre

    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.objects.get(uuid=periodo_uuid)

    if consolidado_dre_uuid:
        consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
    else:
        consolidado_dre = ConsolidadoDRE.objects.get(dre=dre, periodo=periodo,
                                                     sequencia_de_publicacao=sequencia_de_publicacao)

    if not consolidado_dre.eh_retificacao:
        # Uma retificacao ja possui suas PCs vinculadas

        atrelar_pc_ao_consolidado_dre(
            dre=dre,
            periodo=periodo,
            consolidado_dre=consolidado_dre,
        )

    gerar_previa_relatorio_consolidado_dre(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        usuario=usuario,
        parcial=parcial,
        consolidado_dre_uuid=consolidado_dre_uuid,
        sequencia_de_publicacao=sequencia_de_publicacao,
        apenas_nao_publicadas=apenas_nao_publicadas,
    )

    eh_parcial = parcial['parcial']
    consolidado_dre.passar_para_status_gerado(eh_parcial)
