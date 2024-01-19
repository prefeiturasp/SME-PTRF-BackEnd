from celery import shared_task

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs_secundario import simular_logs_secundario


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_secundario_async():
    logger = ContextualLogger.get_logger(__name__, operacao='simulação de logs secundários async')

    simular_logs_secundario(custom_logger=logger)
