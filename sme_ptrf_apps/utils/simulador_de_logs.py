import logging
import random
import time

from sme_ptrf_apps.utils.contextual_logger import ContextualLogger

TEMPO = 30  # segundos


logger = ContextualLogger.get_logger(__name__, operacao='operação simulação de logs')


def simular_logs(segundos=TEMPO):
    end_time = time.time() + TEMPO  # Tempo de execução da task

    logger.info(f'Iniciando o simulador de logs. Irá rodar por {segundos} segundos.', extra={'operacao_id': '1234567890'})

    while time.time() < end_time:
        generate_random_log()
        time.sleep(random.uniform(0.5, 2))  # Espera um tempo aleatório entre 0.5 e 2 segundos


def generate_random_log():
    log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

    log_level = random.choice(log_levels)
    message = f"Log de teste - Nível: {logging.getLevelName(log_level)}"
    logger.log(level=log_level, msg=message)
