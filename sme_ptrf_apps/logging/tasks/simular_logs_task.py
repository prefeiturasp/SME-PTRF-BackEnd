from celery import shared_task

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs import simular_logs


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_async():
    logger = ContextualLogger.get_logger(__name__, operacao='Simulação de logs async')

    simular_logs(logger=logger)
