import logging

from celery import shared_task
from sme_ptrf_apps.core.models import ProcessoAssociacao

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def vincular_processos_async():
    logger.info('Iniciando o vinculo de periodos a processos async.')

    ProcessoAssociacao.vincula_periodos_aos_processos()

    logger.info('Finalizado o vinculo de periodos a processos async.')
