import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_inicio_periodo_prestacao_de_contas_async():
    logger.info('Iniciando task gerar_notificacao_inicio_periodo_prestacao_de_contas_async')

    from sme_ptrf_apps.core.services.notificacao_services import notificar_inicio_periodo_prestacao_de_contas

    logger.info(f'Iniciando a geração de notificação início período prestação de contas async')

    notificar_inicio_periodo_prestacao_de_contas()

    logger.info(f'Finalizando a geração de notificação início período prestação de contas async')
