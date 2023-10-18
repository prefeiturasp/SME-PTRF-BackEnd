import logging

from celery import shared_task
from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_relatorio_devolucao_acertos_async(analise_consolidado_uuid, username, previa):
    logger.info(f"Iniciando geração do relatório de devolução de acertos da sme async")

    from sme_ptrf_apps.dre.services import RelatorioDevolucaoAcertos

    analise_consolidado = AnaliseConsolidadoDre.by_uuid(analise_consolidado_uuid)

    relatorio = RelatorioDevolucaoAcertos(
        analise_consolidado=analise_consolidado,
        username=username,
        previa=previa
    )

    relatorio.gerar_arquivo_relatorio_devolucao_acertos()


    logger.info("Finalizando geração do relatório de devolução de acertos da sme async")