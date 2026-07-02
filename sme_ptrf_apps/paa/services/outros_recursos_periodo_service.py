import logging
from django.db import models
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, Paa, ReceitaPrevistaOutroRecursoPeriodo
from sme_ptrf_apps.paa.enums import PaaStatusAndamentoEnum

logger = logging.getLogger(__name__)


class OutroRecursoPeriodoBaseService:
    def __init__(self, outro_recurso_periodo: OutroRecursoPeriodoPaa) -> None:
        """Inicializa o service com a instância do recurso de período."""
        self.outro_recurso_periodo = outro_recurso_periodo

    def _tinha_todas_unidades(self) -> bool:
        """
        Verifica se o recurso estava disponível para todas as unidades.

        Returns:
            True se não tinha unidades vinculadas (todas as unidades), False caso contrário
        """
        todas = not self.outro_recurso_periodo.unidades.exists()
        logger.debug('Verificando se tinha todas as unidades: ' + str(todas))
        return todas

    def _obtem_paas_afetados(self) -> models.QuerySet:
        """
        Obtem os PAAs afetados pelo recurso do período.

        Returns:
            Lista de PAAs no Período
        """
        paas = Paa.objects.filter(
            periodo_paa=self.outro_recurso_periodo.periodo_paa
        ).select_related('associacao', 'associacao__unidade', 'periodo_paa')
        return paas

    def _paas_afetados_em_elaboracao(self) -> models.QuerySet:
        """Retorna os PAAs afetados com status em elaboração."""
        return self._obtem_paas_afetados().paas_em_elaboracao()

    def _paas_afetados_gerado_retificado(self) -> models.QuerySet:
        """Retorna os PAAs afetados com status gerado ou gerado parcialmente."""
        paas_andamento_gerados = self._obtem_paas_afetados().filter(
            pk=models.OuterRef('id')).paas_gerados()

        paas_andamento_gerados_parcialmente = self._obtem_paas_afetados().filter(
            pk=models.OuterRef('id')).paas_gerados_parcialmente()

        paas_em_retificacao = self._obtem_paas_afetados().filter(
            pk=models.OuterRef('id')).paas_em_retificacao()

        return self._obtem_paas_afetados().filter(
            # É gerado quando o status andamento é Gerado ou Gerado parcialmente(inclui Retificado)
            models.Exists(paas_andamento_gerados) |
            models.Exists(paas_andamento_gerados_parcialmente) |
            models.Exists(paas_em_retificacao),
        )

    def _paa_em_elaboracao(self, paa: Paa) -> bool:
        """
        Verifica se o PAA está em elaboração.

        Args:
            paa: Instância do PAA

        Returns:
            True se estiver em elaboração, False caso contrário
        """
        return paa.get_status_andamento() == PaaStatusAndamentoEnum.EM_ELABORACAO.name

    def _paa_gerado_retificado(self, paa: Paa) -> bool:
        """
        Verifica se o PAA está gerado ou em retificação.

        Args:
            paa: Instância do PAA

        Returns:
            True se estiver gerado ou em retificação
        """
        return paa.get_status_andamento() in [
            PaaStatusAndamentoEnum.GERADO.name,
            PaaStatusAndamentoEnum.GERADO_PARCIALMENTE.name,
            PaaStatusAndamentoEnum.EM_RETIFICACAO.name
        ]

    def _paa_retificado(self, paa: Paa) -> bool:
        """
        Verifica se o PAA está em retificação.

        Args:
            paa: Instância do PAA

        Returns:
            True se estiver em retificação
        """
        em_retificacao = paa.status_em_retificacao
        return em_retificacao

    def _paa_gerado(self, paa: Paa) -> bool:
        """
        Verifica se o PAA está gerado.

        Args:
            paa: Instância do PAA

        Returns:
            True se estiver gerado
        """
        return paa.get_status_andamento() == PaaStatusAndamentoEnum.GERADO.name

    def _receitas_previstas_outro_recurso_periodo_afetadas(self, paa: Paa) -> models.QuerySet:
        """Retorna as receitas previstas do PAA vinculadas ao recurso de período."""
        logger.info(
            f"Buscando receitas previstas de outros recursos para PAA {paa.id} - {str(paa)} "
            f"e outro recurso período {self.outro_recurso_periodo.id} - {str(self.outro_recurso_periodo)}")
        receitas = ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
            paa=paa,
            outro_recurso_periodo=self.outro_recurso_periodo
        )
        for rec in receitas:
            logger.info('receita prevista a remover: %s' % str(rec.__dict__))
        return receitas

    def _remover_receitas_previstas_outro_recurso_periodo(self, paa: Paa) -> int:
        """
        Remove o outro recurso período das receitas previstas

        Args:
            paa: Instância do PAA

        Returns:
            Número de registros removidos
        """
        try:
            receitas_previstas = self._receitas_previstas_outro_recurso_periodo_afetadas(paa)
            count = receitas_previstas.count()
            receitas_previstas.delete()

            return count
        except Exception as e:
            msg_erro = f"Erro ao remover receitas previstas de outros recursos do PAA {str(paa)}: {str(e)}"
            logger.error(
                msg_erro,
                exc_info=True
            )
            raise Exception(msg_erro)

    def _prioridades_afetadas(self, paa: Paa) -> models.QuerySet:
        """Retorna as prioridades do PAA vinculadas ao recurso de período."""
        logger.info(
            f"Buscando prioridades de outros recursos para PAA {paa.id} - {str(paa)} "
            f"e outro recurso período {self.outro_recurso_periodo.id} - {str(self.outro_recurso_periodo)}")
        prioridades = self.outro_recurso_periodo.outro_recurso.prioridadepaa_set.filter(paa=paa)
        for prioridade in prioridades:
            logger.info('prioridade a remover: %s' % str(prioridade.__dict__))
        return prioridades

    def _remover_prioridades_outro_recurso_periodo(self, paa: Paa) -> int:
        """
        Remove o recurso das prioridades e deixa em branco para informar a ação.

        Args:
            paa: Instância do PAA

        Returns:
            Número de prioridades afetadas
        """
        prioridades = self._prioridades_afetadas(paa)
        count = prioridades.count()
        prioridades.update(outro_recurso=None)
        logger.info(f"{count} prioridades alteradas sobre o campo Outros Recursos")
        return count

    def _outro_recurso_periodo_ativo(self) -> bool:
        """Verifica se o recurso de período está ativo."""
        return self.outro_recurso_periodo.ativo
