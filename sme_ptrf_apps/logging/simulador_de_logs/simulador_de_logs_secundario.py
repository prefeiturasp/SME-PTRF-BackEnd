import logging
import random
import time

from sme_ptrf_apps.logging.loggers import ContextualLogger

TEMPO = 30  # segundos


def simular_logs_secundario(segundos=TEMPO, custom_logger=None):
    # logger = logging.getLogger(__name__)

    if not custom_logger:
        logger = ContextualLogger.get_logger(__name__, operacao='operação simulação de logs secundários',
                                                    username='usertest', aplicacao='SigEscola.API',
                                                    observacao='Teste de log secundário.')
    else:
        logger = custom_logger

    end_time = time.time() + TEMPO  # Tempo de execução da task

    logger.info(f'Iniciando o simulador de logs secundários. Irá rodar por {segundos} segundos.', extra={'operacao_id': '1234567890'})

    while time.time() < end_time:
        generate_random_log(logger)
        time.sleep(random.uniform(0.5, 2))  # Espera um tempo aleatório entre 0.5 e 2 segundos

    # logger.exception(f'Erro simulado', exc_info=True, stack_info=True)


def generate_random_log(logger):

    log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

    log_level = random.choice(log_levels)
    message = f"Log de teste - Nível: {logging.getLevelName(log_level)}"
    logger.log(level=log_level, msg=message)
