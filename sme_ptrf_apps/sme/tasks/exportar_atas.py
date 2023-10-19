import logging

from celery import shared_task
from sme_ptrf_apps.core.models.ata import Ata
from sme_ptrf_apps.sme.services.exporta_atas_service import ExportacoesAtasService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_atas_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = Ata.objects.order_by('id')

    try:
        logger.info("Criando arquivo %s pcs_atas.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesAtasService(
            **params,
            nome_arquivo='pcs_atas.csv'
        ).exporta_atas()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")