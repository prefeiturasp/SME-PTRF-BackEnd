import logging
import time

from django.db import connection

logger = logging.getLogger(__name__)


class MedidorPerformance:
    """Log temporário de tempo e queries acumulados desde a criação até cada ponto medido."""

    def __init__(self, nome):
        self.nome = nome
        self._debug_anterior = connection.force_debug_cursor
        connection.force_debug_cursor = False
        self._queries_inicio = len(connection.queries_log)
        self._inicio = time.perf_counter()
        self._t_ant = self._inicio
        self._q_ant = self._queries_inicio

    def marca(self, rotulo):
        tempo = time.perf_counter() - self._inicio
        queries = len(connection.queries_log) - self._queries_inicio
        logger.info(f'[PROFILING {self.nome}] {rotulo}: {tempo:.3f}s acumulados | {queries} queries acumuladas')

    def finaliza(self):
        self.marca('FIM')
        connection.force_debug_cursor = self._debug_anterior

    def delta(self, rotulo):
        q = len(connection.queries_log)
        t = time.perf_counter()
        novas = list(connection.queries_log)[self._q_ant:]
        tempo_sql = sum(float(x['time']) for x in novas)
        logger.info(
            f'[PROFILING] {rotulo}: +{t - self._t_ant:.3f}s total | {tempo_sql:.3f}s em SQL | +{len(novas)} queries')
        for x in sorted(novas, key=lambda x: -float(x['time']))[:3]:
            logger.info(f"    {x['time']}s  {x['sql'][:160]}")
        self._t_ant, self._q_ant = t, q
