import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if 'operacao' not in record.__dict__:
            record.operacao = ''
        if 'operacao_id' not in record.__dict__:
            record.operacao_id = ''
        if 'username' not in record.__dict__:
            record.username = ''
        if 'observacao' not in record.__dict__:
            record.observacao = ''
        return super().format(record)
