import json
import logging
import os
import sys
from unittest import mock
from unittest.mock import MagicMock

import pika
import pytest

from sme_ptrf_apps.logging import handlers
from sme_ptrf_apps.logging.handlers import RabbitMQHandler, _debug


class _Mocker:

    def __init__(self):
        self._patchers = []

    class _Patch:
        def __init__(self, outer):
            self._outer = outer

        def object(self, target, attr, *args, **kwargs):
            p = mock.patch.object(target, attr, *args, **kwargs)
            m = p.start()
            self._outer._patchers.append(p)
            return m

    @property
    def patch(self):
        return self._Patch(self)

    def spy(self, target, attr):
        original = getattr(target, attr)
        return self.patch.object(target, attr, autospec=True, side_effect=original)

    def stopall(self):
        for p in reversed(self._patchers):
            p.stop()


@pytest.fixture
def mocker():
    m = _Mocker()
    yield m
    m.stopall()


@pytest.fixture
def handler():
    h = RabbitMQHandler('host', 'vhost', 'fila', 'user', 'pass', max_retries=3, retry_delay=0.5)
    yield h
    h.connection = None
    h.channel = None
    h.close()


@pytest.fixture
def sleep_mock(mocker):
    return mocker.patch.object(handlers.time, 'sleep')


@pytest.fixture
def blocking_connection(mocker):
    return mocker.patch.object(handlers.pika, 'BlockingConnection')


def _conexao_aberta():
    conn = MagicMock()
    conn.is_open = True
    conn.channel.return_value.is_open = True
    return conn


def _record(msg='mensagem', level=logging.INFO, **extra):
    record = logging.LogRecord('meu.logger', level, '/app/x.py', 10, msg, None, None, func='funcao')
    for k, v in extra.items():
        setattr(record, k, v)
    return record


def test_init_define_atributos_e_defaults():
    h = RabbitMQHandler('h', 'v', 'q', 'u', 'p')
    assert (h.host, h.virtual_host, h.queue, h.username, h.password) == ('h', 'v', 'q', 'u', 'p')
    assert h.max_retries == 3
    assert h.retry_delay == 0.5
    assert h.connection is None and h.channel is None and h._pid is None


def test_debug_escreve_em_stderr(capsys):
    _debug('olá')
    captured = capsys.readouterr()
    assert captured.err == 'olá\n'
    assert captured.out == ''


def test_is_usable_false_quando_pid_diferente(handler):
    handler.connection = _conexao_aberta()
    handler.channel = handler.connection.channel()
    handler._pid = os.getpid() + 1

    assert handler._is_usable() is False
    assert handler.connection is None and handler.channel is None


def test_is_usable_false_sem_conexao(handler):
    handler._pid = os.getpid()
    assert handler._is_usable() is False


def test_is_usable_false_sem_channel(handler):
    handler._pid = os.getpid()
    handler.connection = _conexao_aberta()
    handler.channel = None
    assert handler._is_usable() is False


def test_is_usable_false_conexao_fechada(handler):
    handler._pid = os.getpid()
    handler.connection = _conexao_aberta()
    handler.connection.is_open = False
    handler.channel = MagicMock(is_open=True)
    assert handler._is_usable() is False


def test_is_usable_false_channel_fechado(handler):
    handler._pid = os.getpid()
    handler.connection = _conexao_aberta()
    handler.channel = MagicMock(is_open=False)
    assert handler._is_usable() is False


def test_is_usable_true(handler):
    handler._pid = os.getpid()
    handler.connection = _conexao_aberta()
    handler.channel = handler.connection.channel()
    assert handler._is_usable() is True


def test_safe_close_sem_conexao_nao_falha(handler):
    handler._safe_close_connection()
    assert handler.connection is None and handler.channel is None


def test_safe_close_fecha_conexao_aberta(handler):
    conn = _conexao_aberta()
    handler.connection = conn
    handler.channel = conn.channel()

    handler._safe_close_connection()

    conn.close.assert_called_once()
    assert handler.connection is None and handler.channel is None


def test_safe_close_nao_fecha_conexao_ja_fechada(handler):
    conn = _conexao_aberta()
    conn.is_open = False
    handler.connection = conn

    handler._safe_close_connection()

    conn.close.assert_not_called()
    assert handler.connection is None


def test_safe_close_ignora_excecao_no_close(handler):
    conn = _conexao_aberta()
    conn.close.side_effect = pika.exceptions.ConnectionWrongStateError()
    handler.connection = conn

    handler._safe_close_connection()

    assert handler.connection is None and handler.channel is None


def test_establish_connection_sucesso_primeira_tentativa(handler, blocking_connection, sleep_mock, capsys):
    conn = _conexao_aberta()
    blocking_connection.return_value = conn

    handler._establish_connection()

    assert handler.connection is conn
    assert handler.channel is conn.channel.return_value
    assert handler._pid == os.getpid()
    handler.channel.queue_declare.assert_called_once_with(queue='fila', durable=True)
    sleep_mock.assert_not_called()
    err = capsys.readouterr().err
    assert 'Tentativa 1' in err and 'Conectado ao RabbitMQ' in err


def test_establish_connection_parametros(handler, blocking_connection):
    blocking_connection.return_value = _conexao_aberta()

    handler._establish_connection()

    params = blocking_connection.call_args[0][0]
    assert params.host == 'host'
    assert params.virtual_host == 'vhost'
    assert params.credentials.username == 'user'
    assert params.credentials.password == 'pass'
    assert params.heartbeat == 0
    assert params.socket_timeout == 5
    assert params.blocked_connection_timeout == 10


def test_establish_connection_fecha_conexao_anterior(handler, blocking_connection):
    antiga = _conexao_aberta()
    handler.connection = antiga
    blocking_connection.return_value = _conexao_aberta()

    handler._establish_connection()

    antiga.close.assert_called_once()


def test_establish_connection_retry_com_backoff_exponencial(handler, blocking_connection, sleep_mock):
    conn = _conexao_aberta()
    blocking_connection.side_effect = [
        pika.exceptions.AMQPConnectionError(),
        pika.exceptions.AMQPConnectionError(),
        conn,
    ]

    handler._establish_connection()

    assert handler.connection is conn
    assert blocking_connection.call_count == 3
    assert [c.args[0] for c in sleep_mock.call_args_list] == [0.5, 1.0]


def test_establish_connection_falha_apos_max_retries(handler, blocking_connection, sleep_mock):
    blocking_connection.side_effect = pika.exceptions.AMQPConnectionError('falhou')

    with pytest.raises(ConnectionError) as exc:
        handler._establish_connection()

    assert 'após 3 tentativas' in str(exc.value)
    assert 'falhou' in str(exc.value)
    assert blocking_connection.call_count == 3
    # não dorme após a última tentativa
    assert sleep_mock.call_count == 2
    assert handler.connection is None and handler.channel is None


def test_establish_connection_erro_no_channel_fecha_conexao_e_retenta(handler, blocking_connection, sleep_mock):
    ruim = _conexao_aberta()
    ruim.channel.side_effect = pika.exceptions.AMQPChannelError()
    boa = _conexao_aberta()
    blocking_connection.side_effect = [ruim, boa]

    handler._establish_connection()

    ruim.close.assert_called_once()
    assert handler.connection is boa


def test_establish_connection_delay_nao_acumula_entre_chamadas(handler, blocking_connection, sleep_mock):
    blocking_connection.side_effect = pika.exceptions.AMQPConnectionError()
    for _ in range(2):
        with pytest.raises(ConnectionError):
            handler._establish_connection()

    assert [c.args[0] for c in sleep_mock.call_args_list] == [0.5, 1.0, 0.5, 1.0]
    assert handler.retry_delay == 0.5


def test_establish_connection_excecao_nao_amqp_propaga(handler, blocking_connection):
    blocking_connection.side_effect = ValueError('inesperado')

    with pytest.raises(ValueError):
        handler._establish_connection()


def test_establish_connection_max_retries_um_nao_dorme(blocking_connection, sleep_mock):
    h = RabbitMQHandler('h', 'v', 'q', 'u', 'p', max_retries=1)
    blocking_connection.side_effect = pika.exceptions.AMQPConnectionError()

    with pytest.raises(ConnectionError):
        h._establish_connection()

    sleep_mock.assert_not_called()


def test_build_body_campos_padrao(handler, monkeypatch):
    monkeypatch.setenv('LOG_ENVIRONMENT', 'TESTE')
    body = json.loads(handler._build_body(_record('olá %s'.replace(' %s', ''))))

    assert body['level'] == 'INFO'
    assert body['message'] == 'olá'
    assert body['logger_name'] == 'meu.logger'
    assert body['path_name'] == '/app/x.py'
    assert body['file_name'] == 'x.py'
    assert body['func_name'] == 'funcao'
    assert body['line_number'] == 10
    assert body['module'] == 'x'
    assert body['exc_info'] is None
    assert body['stack_info'] is None
    assert body['aplicacao'] == 'SigEscola.API'
    assert body['ambiente'] == 'TESTE'
    for chave in ('task_id', 'operacao_id', 'operacao', 'username', 'observacao'):
        assert body[chave] is None

    assert len(body['timestamp']) == 23 and body['timestamp'][19] == ','


def test_build_body_ambiente_default(handler, monkeypatch):
    monkeypatch.delenv('LOG_ENVIRONMENT', raising=False)
    body = json.loads(handler._build_body(_record()))
    assert body['ambiente'] == 'NAO_INFORMADO'


def test_build_body_campos_extras(handler):
    record = _record(
        aplicacao='App', task_id='t1', operacao_id='o1', operacao='op', username='fulano', observacao='obs'
    )
    body = json.loads(handler._build_body(record))
    assert body['aplicacao'] == 'App'
    assert body['task_id'] == 't1'
    assert body['operacao_id'] == 'o1'
    assert body['operacao'] == 'op'
    assert body['username'] == 'fulano'
    assert body['observacao'] == 'obs'


def test_build_body_formata_mensagem_com_args(handler):
    record = logging.LogRecord('l', logging.WARNING, 'p.py', 1, 'valor %s e %d', ('a', 2), None)
    body = json.loads(handler._build_body(record))
    assert body['message'] == 'valor a e 2'
    assert body['level'] == 'WARNING'


def test_build_body_com_exc_info(handler):
    try:
        raise ValueError('boom')
    except ValueError:
        record = _record()
        record.exc_info = sys.exc_info()

    body = json.loads(handler._build_body(record))
    assert 'Traceback' in body['exc_info']
    assert 'ValueError: boom' in body['exc_info']


def test_build_body_com_stack_info(handler):
    record = _record()
    record.stack_info = 'pilha'
    assert json.loads(handler._build_body(record))['stack_info'] == 'pilha'


def test_build_body_preserva_unicode(handler):
    body = handler._build_body(_record('ação'))
    assert json.loads(body)['message'] == 'ação'


def test_publish_reutiliza_conexao_utilizavel(handler, mocker):
    handler.channel = MagicMock()
    mocker.patch.object(handler, '_is_usable', return_value=True)
    establish = mocker.patch.object(handler, '_establish_connection')

    handler._publish('corpo')

    establish.assert_not_called()
    handler.channel.basic_publish.assert_called_once_with(exchange='', routing_key='fila', body='corpo')


def test_publish_conecta_quando_nao_utilizavel(handler, mocker):
    mocker.patch.object(handler, '_is_usable', return_value=False)

    def conectar():
        handler.channel = MagicMock()

    establish = mocker.patch.object(handler, '_establish_connection', side_effect=conectar)

    handler._publish('corpo')

    establish.assert_called_once()
    handler.channel.basic_publish.assert_called_once_with(exchange='', routing_key='fila', body='corpo')


def test_emit_publica_corpo_construido(handler, mocker):
    mocker.patch.object(handler, '_build_body', return_value='corpo')
    publish = mocker.patch.object(handler, '_publish')
    handle_error = mocker.patch.object(handler, 'handleError')

    handler.emit(_record())

    publish.assert_called_once_with('corpo')
    handle_error.assert_not_called()


def test_emit_reconecta_e_tenta_uma_vez_em_amqp_error(handler, mocker):
    mocker.patch.object(handler, '_build_body', return_value='corpo')
    publish = mocker.patch.object(handler, '_publish', side_effect=[pika.exceptions.AMQPError(), None])
    close = mocker.patch.object(handler, '_safe_close_connection')
    handle_error = mocker.patch.object(handler, 'handleError')

    handler.emit(_record())

    assert publish.call_count == 2
    close.assert_called_once()
    handle_error.assert_not_called()


def test_emit_reconecta_em_oserror(handler, mocker):
    mocker.patch.object(handler, '_build_body', return_value='corpo')
    publish = mocker.patch.object(handler, '_publish', side_effect=[OSError(), None])
    mocker.patch.object(handler, '_safe_close_connection')
    handle_error = mocker.patch.object(handler, 'handleError')

    handler.emit(_record())

    assert publish.call_count == 2
    handle_error.assert_not_called()


def test_emit_segunda_falha_chama_handle_error_sem_propagar(handler, mocker):
    mocker.patch.object(handler, '_build_body', return_value='corpo')
    publish = mocker.patch.object(handler, '_publish', side_effect=pika.exceptions.AMQPError())
    mocker.patch.object(handler, '_safe_close_connection')
    handle_error = mocker.patch.object(handler, 'handleError')
    record = _record()

    handler.emit(record)

    assert publish.call_count == 2  # apenas uma retentativa
    handle_error.assert_called_once_with(record)


def test_emit_connection_error_do_establish_chama_handle_error(handler, mocker):
    mocker.patch.object(handler, '_build_body', return_value='corpo')
    mocker.patch.object(handler, '_publish', side_effect=ConnectionError('sem broker'))
    handle_error = mocker.patch.object(handler, 'handleError')
    record = _record()

    handler.emit(record)

    handle_error.assert_called_once_with(record)


def test_emit_falha_no_build_body_chama_handle_error(handler, mocker):
    mocker.patch.object(handler, '_build_body', side_effect=TypeError('x'))
    publish = mocker.patch.object(handler, '_publish')
    handle_error = mocker.patch.object(handler, 'handleError')
    record = _record()

    handler.emit(record)

    publish.assert_not_called()
    handle_error.assert_called_once_with(record)


def test_emit_integrado_via_logger(handler, blocking_connection):
    conn = _conexao_aberta()
    blocking_connection.return_value = conn
    log = logging.getLogger('teste.rabbit.integrado')
    log.propagate = False
    log.setLevel(logging.INFO)
    log.addHandler(handler)
    try:
        log.info('olá', extra={'username': 'fulano'})
    finally:
        log.removeHandler(handler)

    publish = conn.channel.return_value.basic_publish
    publish.assert_called_once()
    kwargs = publish.call_args.kwargs
    assert kwargs['routing_key'] == 'fila' and kwargs['exchange'] == ''
    body = json.loads(kwargs['body'])
    assert body['message'] == 'olá' and body['username'] == 'fulano'


def test_emit_segunda_chamada_reutiliza_conexao(handler, blocking_connection):
    blocking_connection.return_value = _conexao_aberta()

    handler.emit(_record('a'))
    handler.emit(_record('b'))

    assert blocking_connection.call_count == 1
    assert handler.channel.basic_publish.call_count == 2


def test_emit_apos_fork_abre_nova_conexao(handler, blocking_connection):
    blocking_connection.return_value = _conexao_aberta()
    handler.emit(_record('a'))
    handler._pid = os.getpid() + 1  # simula processo filho

    handler.emit(_record('b'))

    assert blocking_connection.call_count == 2


# ----------------------------------------------------------------- close
def test_close_fecha_conexao_e_chama_super(handler, mocker):
    conn = _conexao_aberta()
    handler.connection = conn
    handler.channel = conn.channel()
    super_close = mocker.spy(logging.Handler, 'close')

    handler.close()

    conn.close.assert_called_once()
    assert handler.connection is None and handler.channel is None
    super_close.assert_called_once()


def test_close_tolerante_sem_conexao(handler):
    handler.close()
    handler.close()


def test_close_tolerante_a_erro_no_close_da_conexao(handler):
    conn = _conexao_aberta()
    conn.close.side_effect = Exception('já fechada')
    handler.connection = conn

    handler.close()

    assert handler.connection is None


def test_close_libera_lock_mesmo_com_erro(handler, mocker):
    mocker.patch.object(handler, '_safe_close_connection', side_effect=RuntimeError('x'))

    with pytest.raises(RuntimeError):
        handler.close()

    # lock reentrante liberado: outra aquisição/liberação funciona normalmente
    handler.acquire()
    handler.release()


def test_emit_nao_propaga_falha_de_conexao(handler, blocking_connection, sleep_mock, mocker):
    blocking_connection.side_effect = pika.exceptions.StreamLostError('Transport indicated EOF')
    handle_error = mocker.patch.object(handler, 'handleError')
    record = _record()

    handler.emit(record)

    # apenas um ciclo de max_retries; sem retentativa extra do emit
    assert blocking_connection.call_count == 3
    handle_error.assert_called_once_with(record)
