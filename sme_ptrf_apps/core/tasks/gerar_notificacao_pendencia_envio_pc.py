import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_pendencia_envio_prestacao_de_contas_async():
    logger.info(f'Iniciando a geração de notificação pendência envio prestação de contas async')

    from sme_ptrf_apps.core.services.notificacao_services import notificar_pendencia_envio_prestacao_de_contas

    notificar_pendencia_envio_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação pendência envio prestação de contas async')
