import logging

from celery import shared_task

from django.db.models import Q, Value
from django.db.models.functions import Replace

from sme_ptrf_apps.core.models import (
    Ata,
    Participante
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def migrar_campos_presidente_secretario_atas_async():
    logger.info(f"Iniciando serviço de atualização em massa de regularidade")
    atualizar_presidente_e_secretario()
    logger.info(f"Finalizado serviço de atualização em massa de regularidade")


def remover_tag_ajustar_das_atas():
    # Atualiza o campo comentarios, removendo a substring '**ajustar**'
    Ata.objects.filter(comentarios__icontains='**ajustar**').update(
        comentarios=Replace('comentarios', Value('**ajustar**'), Value(''))
    )


def atualizar_presidente_e_secretario():

    remover_tag_ajustar_das_atas()

    atas_sem_presidente_secretario = Ata.objects.filter(
        Q(presidente_da_reuniao__isnull=True) | Q(secretario_da_reuniao__isnull=True)
    )

    atas_nao_atualizadas = []
    for ata in atas_sem_presidente_secretario:
        logger.info(f"Ata ID {ata.id}...")

        presidente_atualizado = True
        secretario_atualizado = True
        salvar_ata = False

        if ata.presidente_reuniao and not ata.presidente_da_reuniao:
            # Atualizar presidente
            presidente = Participante.objects.filter(nome__unaccent__icontains=ata.presidente_reuniao, ata=ata).first()
            if presidente:
                ata.presidente_da_reuniao = presidente
                salvar_ata = True
            else:
                presidente_atualizado = False
                logger.warning(f"Presidente não encontrado para a ata ID {ata.id} com nome {ata.presidente_reuniao}.")

        if ata.secretario_reuniao and not ata.secretario_da_reuniao:
            # Atualizar secretário
            secretario = Participante.objects.filter(nome__unaccent__icontains=ata.secretario_reuniao, ata=ata).first()
            if secretario:
                ata.secretario_da_reuniao = secretario
                salvar_ata = True
            else:
                logger.warning(f"Secretário não encontrado para a ata ID {ata.id} com nome {ata.secretario_reuniao}.")
                secretario_atualizado = False

        if not presidente_atualizado or not secretario_atualizado:
            if ata.comentarios is None:
                ata.comentarios = '**rever**'
            else:
                ata.comentarios = f'{ata.comentarios} **rever**'

            salvar_ata = True

            atas_nao_atualizadas.append(ata)

        # Salva a ata se algum dos campos foi atualizado
        if salvar_ata:
            ata.save()

    if atas_nao_atualizadas:
        logger.warning(f"Não foi possível atualizar todos as atas. Qtd não atualizada: {len(atas_nao_atualizadas)}. Filtre por **rever**.")
    else:
        logger.info("Todos os presidentes e secretários foram atualizados com sucesso.")
