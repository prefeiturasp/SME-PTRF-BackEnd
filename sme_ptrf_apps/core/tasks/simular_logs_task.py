from celery import shared_task

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.logging.simulador_de_logs import simular_logs


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_async():
    logger = ContextualLogger.get_logger(__name__, task_logger=True, operacao='operação simulação de logs', operacao_id='271170',
                                         username='usertest', aplicacao='SigEscola.API', observacao='observação teste')

    simular_logs(custom_logger=logger)
