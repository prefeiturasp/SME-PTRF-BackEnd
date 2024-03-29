import logging

from celery import shared_task
from sme_ptrf_apps.sme.services.exporta_saldo_final_periodo_pc_service import ExportacoesDadosSaldosFinaisPeriodoService
from sme_ptrf_apps.core.models import FechamentoPeriodo

logger = logging.getLogger(__name__)

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_saldos_finais_periodo_async(data_inicio, data_final, username, dre_uuid=None):
    logger.info("Exportando csv em processamento...")

    if dre_uuid:
        queryset = FechamentoPeriodo.objects.filter(
            associacao__unidade__dre__uuid=dre_uuid,
        ).order_by('id')
    else:
        queryset = FechamentoPeriodo.objects.all().order_by('id')

    try:
        logger.info("Criando arquivo %s pcs_saldo_final_periodo.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDadosSaldosFinaisPeriodoService(
            **params,
            nome_arquivo='pcs_saldo_final_periodo.csv'
        ).exporta_saldos_finais_periodos()
    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
