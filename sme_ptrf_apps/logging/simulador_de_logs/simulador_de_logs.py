import logging
import random
import time

from sme_ptrf_apps.logging.decorators import with_contextual_logger

TEMPO = 30  # segundos


@with_contextual_logger(
    operacao='Simulação de logs',
    operacao_id='logs_sync',
    aplicacao='SigEscola.API',
    username='joselito',
    observacao='obs geral do logger.'
)
def simular_logs(segundos=TEMPO, logger=None):
    end_time = time.time() + TEMPO  # Tempo de execução da task
    qtd_logs = 0

    logger.info(f'Iniciando o simulador de logs. Irá rodar por {segundos} segundos.', extra={'observacao': 'teste definição da obs no log.'})
    qtd_logs += 1

    while time.time() < end_time:
        generate_random_log(logger)
        qtd_logs += 1

    # Em logs de erro, é possível passar o traceback para o logger
    # logger.exception(f'Erro simulado', exc_info=True, stack_info=True)

    print(f'Quantidade de logs gerados: {qtd_logs}')
    print(f'Quantidade de logs por segundo: {qtd_logs/TEMPO}')
    print(f'Tempo médio de geração de logs: {TEMPO/qtd_logs}')


def generate_random_log(logger):

    log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

    log_level = random.choice(log_levels)
    message = f"Log de teste - Nível: {logging.getLevelName(log_level)}"
    logger.log(level=log_level, msg=message)
