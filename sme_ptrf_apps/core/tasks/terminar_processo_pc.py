from celery import shared_task

from sme_ptrf_apps.core.models import TaskCelery
from sme_ptrf_apps.logging.loggers import ContextualLogger


@shared_task(
    bind=True,
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def terminar_processo_pc_async(
    self,
    periodo_uuid,
    associacao_uuid,
    username="",
    id_task=None,
):
    from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

    logger_terminar_pc = ContextualLogger.get_logger(
        __name__,
        operacao='Prestação de Contas',
        username=username,
        task_id=str(id_task),
    )

    task = TaskCelery.objects.get(uuid=id_task)

    task.registra_task_assincrona(self.request.id)

    # Apenas para informar que os logs não mais ficarão registrados na task.
    task.grava_log_concatenado('Iniciando a task terminar_processo_pc_async. Logs registrados apenas no Kibana.')

    pc_service = PrestacaoContaService(
        periodo_uuid=periodo_uuid,
        associacao_uuid=associacao_uuid,
        username=username,
        logger=logger_terminar_pc
    )

    logger_terminar_pc.info(f'Iniciando a task terminar_processo_pc_async.')
    pc_service.terminar_processo_pc()
    logger_terminar_pc.info(f'Task terminar_processo_pc_async finalizada com sucesso.')

    task.registra_data_hora_finalizacao('Task terminar_processo_pc_async finalizada com sucesso.')
