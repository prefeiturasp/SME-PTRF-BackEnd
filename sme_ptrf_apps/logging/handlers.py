import os
import sys
import time
import logging
import pika
import json
import traceback
import environ

from datetime import datetime

env = environ.Env()


def _debug(msg):
    # print em stderr; nunca usar logging aqui para evitar recursão
    print(msg, file=sys.stderr)


class RabbitMQHandler(logging.Handler):
    def __init__(self, host, virtual_host, queue, username, password, max_retries=3, retry_delay=0.5):
        super().__init__()
        self.host = host
        self.virtual_host = virtual_host
        self.queue = queue
        self.username = username
        self.password = password
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.channel = None
        self._pid = None

    def _is_usable(self):
        if self._pid != os.getpid():
            self.connection = None
            self.channel = None
            return False
        return (
            self.connection is not None and self.connection.is_open
            and self.channel is not None and self.channel.is_open
        )

    def _safe_close_connection(self):
        conn = self.connection
        self.connection = None
        self.channel = None
        if conn is None:
            return
        try:
            if conn.is_open:
                conn.close()
        except Exception:
            pass  # já fechada pelo broker / outro estado inválido

    def _establish_connection(self):
        self._safe_close_connection()
        delay = self.retry_delay
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            _debug(f"Tentando conectar ao RabbitMQ: {self.host} - {self.virtual_host} - {self.queue}. Tentativa {attempt}")
            try:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    virtual_host=self.virtual_host,
                    credentials=credentials,
                    heartbeat=0,  # handler não processa eventos; evita o broker derrubar por heartbeat
                    socket_timeout=5,
                    blocked_connection_timeout=10,
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)
                self._pid = os.getpid()
                _debug(f"Conectado ao RabbitMQ: {self.host} - {self.virtual_host} - {self.queue}")
                return
            except pika.exceptions.AMQPError as e:
                last_error = e
                self._safe_close_connection()
                if attempt < self.max_retries:
                    time.sleep(delay)
                    delay *= 2  # backoff exponencial

        raise ConnectionError(
            f"Não foi possível estabelecer conexão com o RabbitMQ após {self.max_retries} tentativas: {last_error}"
        )


    def _build_body(self, record):
        if record.exc_info:
            exc_type, exc_value, exc_traceback = record.exc_info
            exc_info_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        else:
            exc_info_str = None

        return json.dumps({
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
            'stack_info': record.stack_info if record.stack_info else None,
            'aplicacao': getattr(record, 'aplicacao', 'SigEscola.API'),
            'task_id': getattr(record, 'task_id', None),
            'ambiente': env('LOG_ENVIRONMENT', default='NAO_INFORMADO'),
            'operacao_id': getattr(record, 'operacao_id', None),
            'operacao': getattr(record, 'operacao', None),
            'username': getattr(record, 'username', None),
            'observacao': getattr(record, 'observacao', None),
        })

    def _publish(self, body):
        if not self._is_usable():
            self._establish_connection()
        self.channel.basic_publish(exchange='', routing_key=self.queue, body=body)

    def emit(self, record):
        # Nunca deixar falha de log propagar para a aplicação
        try:
            body = self._build_body(record)

            try:
                self._publish(body)

            except ConnectionError:
                raise

            except (pika.exceptions.AMQPError, OSError):
                self._safe_close_connection()
                self._publish(body)

        except Exception:
            self.handleError(record)

    def close(self):
        # Chamado pelo logging.shutdown / reconfiguração (ex.: Celery import_modules).
        # Tem que ser tolerante a conexão já fechada.
        self.acquire()
        try:
            self._safe_close_connection()
        finally:
            self.release()
        super().close()