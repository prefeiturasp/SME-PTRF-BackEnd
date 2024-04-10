import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from sme_ptrf_apps.core.models import (
    Ata,
    Participante
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=333333,
    soft_time_limit=333333
)
def migrar_campos_presidente_secretario_atas_async():
    logger.info(f"Iniciando serviço de atualização em massa de regularidade")
    atualizar_presidente_e_secretario()
    logger.info(f"Finalizado serviço de atualização em massa de regularidade")


def atualizar_presidente_e_secretario():
    atas_sem_presidente_secretario = Ata.objects.filter(presidente_da_reuniao__isnull=True,
                                                        secretario_da_reuniao__isnull=True)

    atas_nao_atualizadas = []
    for ata in atas_sem_presidente_secretario:
        logger.info(f"Ata ID {ata.id}...")

        ata_atualizada = True

        if ata.presidente_reuniao:
            # Atualizar presidente
            presidente = Participante.objects.filter(nome=ata.presidente_reuniao, ata=ata).first()
            if presidente:
                ata.presidente_da_reuniao = presidente
            else:
                ata_atualizada = False
                logger.warning(f"Presidente não encontrado para a ata ID {ata.id} com nome {ata.presidente_reuniao}.")

        if ata.secretario_reuniao:
            # Atualizar secretário
            secretario = Participante.objects.filter(nome=ata.secretario_reuniao, ata=ata).first()
            if secretario:
                ata.secretario_da_reuniao = secretario
            else:
                logger.warning(f"Secretário não encontrado para a ata ID {ata.id} com nome {ata.secretario_reuniao}.")
                ata_atualizada = False

        if not ata_atualizada:
            if ata.comentarios is None:
                ata.comentarios = '**rever**'
            else:
                ata.comentarios = f'{ata.comentarios} **rever**'

            ata.save()

            atas_nao_atualizadas.append(ata)

        # Salva a ata se algum dos campos foi atualizado
        if ata.presidente_da_reuniao or ata.secretario_da_reuniao:
            ata.save()

    if atas_nao_atualizadas:
        logger.warning(f"Não foi possível atualizar todos as atas. Qtd não atualizada: {len(atas_nao_atualizadas)}. Filtre por **rever**.")
    else:
        logger.info("Todos os presidentes e secretários foram atualizados com sucesso.")
