from celery import shared_task

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs_secundario import simular_logs_secundario


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_secundario_async():
    task_id = simular_logs_secundario_async.request.id
    logger = ContextualLogger.get_logger(
        __name__,
        operacao='Simulação de logs secundários async',
        operacao_id='logs_async',
        aplicacao='SigEscola.tasks',
        username='pedro',
        observacao='obs geral do logger task secundaria.',
        task_id=task_id,
    )

    simular_logs_secundario(logger=logger)
