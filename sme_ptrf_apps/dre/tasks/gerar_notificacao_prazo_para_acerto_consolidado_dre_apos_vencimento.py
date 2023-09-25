import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_notificacao_prazo_para_acerto_consolidado_dre_apos_vencimento_async():
    logger.info(f'Iniciando a geração de notificação prazo acerto apos vencimento async')

    from sme_ptrf_apps.dre.services.notificacao_service.notificacao_prazo_para_acerto_consolidado_devolucao import NotificacaoConsolidadoPrazoAcertoVencimento
    NotificacaoConsolidadoPrazoAcertoVencimento().notificar_prazo_para_acerto_apos_vencimento()

    logger.info(f'Finalizando a geração de notificação prazo acerto apos vencimento async')
