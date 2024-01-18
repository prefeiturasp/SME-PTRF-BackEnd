import logging
import environ

from sme_ptrf_apps.logging.handlers import RabbitMQHandler

env = environ.Env()

enable_rabbitmq_logging = env.bool("ENABLE_RABBITMQ_LOGGING", default=False)


class ContextualLogger(logging.LoggerAdapter):
    """
    Um adaptador de logger que adiciona contexto adicional a cada log.
    """
    def __init__(self, logger, extra=None):
        # Assegure que extra é sempre um dicionário
        if extra is None:
            extra = {}
        elif not isinstance(extra, dict):
            raise ValueError("Extra context must be a dictionary")
        super().__init__(logger, extra)

    def process(self, msg, kwargs):
        # Obter contexto adicional do log atual, se houver
        additional_context = kwargs.pop('extra', {})

        if not isinstance(additional_context, dict):
            raise ValueError("additional_context precisa ser um dicionário")

        # Preparar o contexto final combinando os contextos
        combined_context = {**self.extra, **additional_context}
        kwargs['extra'] = combined_context

        return msg, kwargs

    @classmethod
    def _get_logger(cls, name, **kwargs):
        """
        Retorna um logger com contexto adicional.
        """
        logger = logging.getLogger(name)
        context = {k: v for k, v in kwargs.items() if v is not None}
        return cls(logger, context)

    @classmethod
    def get_logger(cls, name, task_logger=False, **kwargs):
        """
        Retorna um logger com contexto adicional. Se task_logger for True, o nome do logger será 'task_<name>'.
        Espera-se que a configuração de logging do projeto names iniciados com task_ não tenham o RabbitMQHandler
        para que ele seja criado aqui e seja um para cada task.
        """
        print('Getting logger')
        logger_name = f'api_{name}' if not task_logger else f'task_{name}'
        logger = cls._get_logger(logger_name, **kwargs)
        if task_logger:
            print('Conectando ao RabbitMQ em logger de task.')
            # remove o handler RabbitMQHandler padrão se existir na lista de handlers do logger
            logger.logger.handlers = [handler for handler in logger.logger.handlers if not isinstance(handler, RabbitMQHandler)]

            # cria um novo handler RabbitMQHandler exclusivo para o logger da task
            rabbitmq_handler = RabbitMQHandler(
                host=env("RABBITMQ_HOST"),
                virtual_host=env("RABBITMQ_VIRTUAL_HOST"),
                queue=env("RABBITMQ_LOG_QUEUE"),
                username=env("RABBITMQ_USERNAME"),
                password=env("RABBITMQ_PASSWORD")
            )
            logger.logger.addHandler(rabbitmq_handler)

        return logger
