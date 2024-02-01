import functools
from sme_ptrf_apps.logging.loggers import ContextualLogger


def with_contextual_logger(**logger_kwargs):
    """
    Decorator que adiciona um logger contextual a uma função se um logger não for passado como argumento.
    :param logger_kwargs: kwargs para o logger contextual
    :return: decorator

    Exemplo de uso:
    @with_contextual_logger(operacao='operação simulação de logs', aplicacao='SigEscola.API')
    def simular_logs(segundos=TEMPO, custom_logger=None):
        ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if 'logger' not in kwargs or kwargs['logger'] is None:
                module_name = func.__module__  # Pega o nome do módulo da função decorada
                kwargs['logger'] = ContextualLogger.get_logger(
                    module_name, **logger_kwargs
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
