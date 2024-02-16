import logging
import environ

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
            raise ValueError("Extra precisa ser um dicionário")
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

    def update_context(self, **new_context):
        """
        Atualiza o contexto do logger com novas ou modificadas propriedades.
        """
        self.extra.update(new_context)

        for key in list(self.extra.keys()):
            if not isinstance(key, str):
                raise ValueError("Todas as chaves do contexto devem ser strings")

    @classmethod
    def _get_logger(cls, name, **kwargs):
        """
        Retorna um logger com contexto adicional.
        """
        logger = logging.getLogger(name)
        context = {k: v for k, v in kwargs.items() if v is not None}
        return cls(logger, context)

    @classmethod
    def get_logger(cls, name, **kwargs):
        """
        Retorna um logger com contexto adicional. Acrescenta o prefixo 'api_' para identificar que é um ContextualLogger
        """
        logger_name = f'api_{name}'
        logger = cls._get_logger(logger_name, **kwargs)

        return logger
