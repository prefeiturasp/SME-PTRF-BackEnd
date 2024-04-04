import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models import Repasse
from sme_ptrf_apps.sme.services.exporta_repasses_service import ExportacaoDadosRepassesService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_repasses_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")
    queryset = Repasse.objects.all()
    try:
        logger.info("Criando arquivo %s repasses.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username
        }
        ExportacaoDadosRepassesService(
            **params,
            nome_arquivo='repasses.csv'
        ).exporta_repasses()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
