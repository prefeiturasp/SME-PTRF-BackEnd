from celery import shared_task

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.logging.simulador_de_logs.simulador_de_logs import simular_logs


@shared_task(
    time_limet=90,
    soft_time_limit=120
)
def simular_logs_async():
    task_id = simular_logs_async.request.id
    logger = ContextualLogger.get_logger(
        __name__,
        operacao='Simulação de logs async',
        operacao_id='logs_async',
        aplicacao='SigEscola.tasks',
        username='mariazinha',
        observacao='obs geral do logger task.',
        task_id=str(task_id),
    )

    simular_logs(logger=logger)
