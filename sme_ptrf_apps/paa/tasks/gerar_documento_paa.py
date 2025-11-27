from django.contrib.auth import get_user_model
from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError
from sme_ptrf_apps.paa.services.documento_paa_pdf_service import gerar_arquivo_documento_paa_pdf
from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.paa.models.paa import Paa
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa

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
def gerar_documento_paa_async(self, paa_uuid, username=""):
    logger = ContextualLogger.get_logger(
        __name__,
        operacao='Plano Anual de Atividades',
        username=username
    )
    tentativa = current_task.request.retries + 1

    try:
        logger.info(f'Iniciando task gerar_documento_paa_async, tentativa {tentativa}.')

        paa = Paa.objects.get(uuid=paa_uuid)

        usuario = get_user_model().objects.get(username=username)

        # apagar documentos anteriores
        documento_paa, _ = DocumentoPaa.objects.get_or_create(paa=paa, versao=DocumentoPaa.VersaoChoices.FINAL)
        logger.info('Documento PAA criado')

        documento_paa.arquivo_em_processamento()
        logger.info('Documento PAA em processamento')

        gerar_arquivo_documento_paa_pdf(paa, documento_paa, usuario, previa=False)

        documento_paa.arquivo_concluido()
        logger.info(f'Documento PAA arquivo {documento_paa.uuid}.')

        logger.info('Task gerar_documento_paa_async finalizada.')
    except Exception as exc:
        logger.error(
            f'A tentativa {tentativa} de gerar o documento PAA falhou.',
            exc_info=True,
            stack_info=True
        )

        if tentativa > MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas para o documento PAA.'
            logger.error(
                mensagem_tentativas_excedidas,
                exc_info=True,
                stack_info=True
            )

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc
