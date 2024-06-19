import logging

from celery import shared_task
from sme_ptrf_apps.despesas.services.despesa_service import migra_despesas_periodos_anteriores

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def migrar_gastos_periodos_anteriores_async():
    logger.info('Iniciando a task de migração de gastos de períodos anteriores.')

    migra_despesas_periodos_anteriores()

    logger.info('Finalizado a task de migração de gastos de períodos anteriores.')
