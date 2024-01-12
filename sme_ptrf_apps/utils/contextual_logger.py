import logging


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
    def get_logger(cls, name, operacao=None, operacao_id=None, username=None, observacao=None):
        """
        Retorna um logger com contexto adicional.
        """
        logger = logging.getLogger(name)
        context = {
            'operacao': operacao,
            'operacao_id': operacao_id,
            'username': username,
            'observacao': observacao,
        }
        # Filtra fora valores None para manter o contexto limpo
        context = {k: v for k, v in context.items() if v is not None}
        return cls(logger, context)
