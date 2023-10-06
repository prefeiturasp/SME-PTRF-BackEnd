import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_encerramento_conta_bancaria_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_encerramento_conta_bancaria

    logger.info('Iniciando a geração de notificação de encerramento conta bancaria async.')

    notificar_encerramento_conta_bancaria()

    logger.info('Executado serviço de notificação de encerramento conta bancaria async.')
