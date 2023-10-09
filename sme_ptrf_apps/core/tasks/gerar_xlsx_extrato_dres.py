import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_xlsx_extrato_dres_async(periodo_uuid, conta_uuid, username):
    logger.info('Iniciando a exportação do arquivo xlsx de extratos dres async')
    from sme_ptrf_apps.sme.services.exporta_arquivos_service import gerar_arquivo_xlsx_extrato_dres
    from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download, atualiza_arquivo_download, atualiza_arquivo_download_erro

    obj_arquivo_download = gerar_arquivo_download(username, "saldos_bancarios_associacoes.xlsx")
    try:
        arquivo_xlsx = gerar_arquivo_xlsx_extrato_dres(periodo_uuid, conta_uuid, username)
        atualiza_arquivo_download(obj_arquivo_download, arquivo_xlsx)
    except Exception as e:
        atualiza_arquivo_download_erro(obj_arquivo_download, e)

    logger.info('Finalizando a exportação do arquivo xlsx de saldos bancarios em detalhes associações async')
