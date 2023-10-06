import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    PrestacaoConta,
    Ata,
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_arquivo_ata_async(prestacao_de_contas_uuid, ata_uuid, usuario):
    logger.info('Iniciando task gerar_arquivo_ata_async')

    logger.info(f'Iniciando criação do Arquivo da Ata, prestação {prestacao_de_contas_uuid} e ata {ata_uuid}')
    from sme_ptrf_apps.core.services.ata_service import gerar_arquivo_ata

    prestacao_de_contas = PrestacaoConta.by_uuid(prestacao_de_contas_uuid)
    ata = Ata.by_uuid(ata_uuid)

    arquivo_ata = gerar_arquivo_ata(prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata: {arquivo_ata} gerado com sucesso.')
