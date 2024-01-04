import logging


from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def terminar_processo_pc_async(
    periodo_uuid,
    associacao_uuid,
    username="",
):
    from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

    logger.info(f'Iniciando a task terminar_processo_pc_async')

    pc_service = PrestacaoContaService(
        periodo_uuid=periodo_uuid,
        associacao_uuid=associacao_uuid,
        username=username,
    )

    pc_service.terminar_processo_pc()

