import time
import logging
import pika
import json
import traceback
import environ

from datetime import datetime

env = environ.Env()


class RabbitMQHandler(logging.Handler):
    def __init__(self, host, virtual_host, queue, username, password, max_retries=5, retry_delay=1):
        super().__init__()
        self.host = host
        self.virtual_host = virtual_host
        self.queue = queue
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _establish_connection(self):
        for _ in range(self.max_retries):
            print(f"Tentando conectar ao RabbitMQ: {self.host} - {self.virtual_host} - {self.queue}. Tentativa {_ + 1}")
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(host=self.host, virtual_host=self.virtual_host,
                                                       credentials=credentials)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                print(f"Conectado ao RabbitMQ xx: {self.host} - {self.virtual_host} - {self.queue}")
                return
            except pika.exceptions.AMQPConnectionError:
                print(f"Não foi possível estabelecer conexão com o RabbitMQ. Tentando novamente em {self.retry_delay} segundos.")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2  # Backoff exponencial

        raise Exception("Não foi possível estabelecer conexão com o RabbitMQ após várias tentativas.")

    def emit(self, record):
        try:
            if not hasattr(self, 'connection') or self.connection.is_closed:
                self._establish_connection()

            if record.exc_info:
                exc_type, exc_value, exc_traceback = record.exc_info
                exc_info_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            else:
                exc_info_str = None

            stack_info_str = record.stack_info if record.stack_info else None

            body = json.dumps({
                'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S,%f')[:-3],
                'level': record.levelname,
                'message': record.getMessage(),
                'logger_name': record.name,
                'path_name': record.pathname,
                'file_name': record.filename,
                'func_name': record.funcName,
                'line_number': record.lineno,
                'module': record.module,
                'process': record.process,
                'process_name': record.processName,
                'thread': record.thread,
                'thread_name': record.threadName,
                'exc_info': exc_info_str,
                'stack_info': stack_info_str,
                'ambiente': env('LOG_ENVIRONMENT', default='NAO_INFORMADO'),
                'operacao_id': record.operacao_id if hasattr(record, 'operacao_id') else None,
                'operacao': record.operacao if hasattr(record, 'operacao') else None,
                'username': record.username if hasattr(record, 'username') else None,
                'aplicacao': record.aplicacao if hasattr(record, 'aplicacao') else None,
                'observacao': record.observacao if hasattr(record, 'observacao') else None,
            })
            self.channel.basic_publish(exchange='', routing_key=self.queue, body=body)

        except (pika.exceptions.AMQPConnectionError, pika.exceptions.ChannelError) as e:
            self._establish_connection()  # Tentar reconectar
            self.emit(record)  # Tentar reenviar o log

    def close(self):
        if hasattr(self, 'connection'):
            print(f"Fechando conexão com RabbitMQ: {self.host} - {self.virtual_host} - {self.queue}")
            self.connection.close()
        super().close()
