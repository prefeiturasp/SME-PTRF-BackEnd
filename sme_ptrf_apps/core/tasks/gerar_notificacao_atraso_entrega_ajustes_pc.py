import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_atraso_entrega_ajustes_prestacao_de_contas_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_atraso_entrega_ajustes_prestacao_de_contas
    logger.info('Iniciando a geração de notificação de atraso na entrega de ajustes de prestações de contas async.')

    notificar_atraso_entrega_ajustes_prestacao_de_contas()

    logger.info('Finalizando a geração de notificação de atraso na entrega de ajustes de prestações de contas async.')

