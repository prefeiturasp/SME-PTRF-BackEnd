import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_proximidade_fim_prazo_ajustes_prestacao_conta_async():
    from sme_ptrf_apps.core.services.notificacao_services import notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas

    logger.info('Iniciando a geração de notificação de proximidade do fim do prazo para entrega de ajustes de prestação de contas async.')

    notificar_proximidade_fim_prazo_ajustes_prestacao_de_contas()

    logger.info('Finalizando a geração de notificação de proximidade do fim do prazo para entrega de ajustes de prestação de contas async.')
