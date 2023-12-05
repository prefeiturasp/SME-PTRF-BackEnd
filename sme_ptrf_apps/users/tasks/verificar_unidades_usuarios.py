import logging
from celery import shared_task
from sme_ptrf_apps.users.services import VerificaUnidadesUsuariosService
from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=333333,
    soft_time_limit=333333
)
def verifica_unidades_usuarios_async():
    logger.info("Iniciando tarefa de verificação de unidades dos usuários async")

    flags = get_waffle_flag_model()

    logger.info("Verificando se a flag <gestao-usuarios> está ativa...")

    if flags.objects.filter(name='gestao-usuarios', everyone=True).exists():
        logger.info("A flag está ativa, o processo de verificação será iniciado...")

        VerificaUnidadesUsuariosService().iniciar_processo()

        logger.info(f'Finalizando a tarefa de verificação de unidades dos usuários async')
    else:
        logger.info("A flag NÃO está ativa, portanto o processo não será iniciado")

