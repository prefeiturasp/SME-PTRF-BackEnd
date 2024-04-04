import logging

from celery import shared_task
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.sme.services.exporta_dados_processos_sei_regularidade_service import ExportaDadosProcessosSeiRegularidadeService

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_processos_sei_regularidade_async(username):
    logger.info("Exportando csv em processamento...")
    queryset = Associacao.objects.all()
    try:
        logger.info("Criando arquivo %s processo_sei_regularidade.csv")
        params = {
            'queryset': queryset,
            'user': username
        }
        ExportaDadosProcessosSeiRegularidadeService(
            **params,
            nome_arquivo='processo_sei_regularidade.csv'
        ).exportar()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")
