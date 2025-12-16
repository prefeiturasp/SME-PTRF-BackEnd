from django.contrib.auth import get_user_model
from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.paa.models import AtaPaa
from sme_ptrf_apps.paa.services.ata_paa_service import gerar_arquivo_ata_paa

MAX_RETRIES = 3


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': MAX_RETRIES},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=600,
    soft_time_limit=300
)
def gerar_ata_paa_async(self, ata_paa_uuid, username=""):
    """
    Task assíncrona para gerar o arquivo PDF da ata PAA final
    """
    logger = ContextualLogger.get_logger(
        __name__,
        operacao='Ata de Apresentação do PAA',
        username=username
    )
    tentativa = current_task.request.retries + 1

    logger.info(f'Iniciando task gerar_ata_paa_async, tentativa {tentativa}.')

    try:
        ata_paa = AtaPaa.objects.get(uuid=ata_paa_uuid)
        usuario = get_user_model().objects.get(username=username) if username else None

        arquivo_ata = gerar_arquivo_ata_paa(ata_paa=ata_paa, usuario=usuario)

        if arquivo_ata is not None:
            logger.info(f'Arquivo ata PAA {arquivo_ata.uuid} gerado com sucesso.')
        else:
            raise Exception("Falha ao gerar arquivo da ata PAA")

        logger.info('Task gerar_ata_paa_async finalizada.')
    except Exception as exc:
        logger.error(
            f'A tentativa {tentativa} de gerar a ata PAA falhou.',
            exc_info=True,
            stack_info=True
        )

        if tentativa > MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas para a ata PAA.'
            logger.error(
                mensagem_tentativas_excedidas,
                exc_info=True,
                stack_info=True
            )

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc

