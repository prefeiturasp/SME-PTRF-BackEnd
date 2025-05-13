import logging
from celery import shared_task
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.sme.services.exporta_dados_membros_apm_legado_service import ExportacaoDadosMembrosApmLegadoService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_dados_membros_apm_legado_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")
    queryset = MembroAssociacao.objects.all()

    try:
        logger.info("Criando arquivo %s membros_apm.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username
        }
        ExportacaoDadosMembrosApmLegadoService(
            **params,
            nome_arquivo='membros_apm.csv'
        ).exporta_membros_apm()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
