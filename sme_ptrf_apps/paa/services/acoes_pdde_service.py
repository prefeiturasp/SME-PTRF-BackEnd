import logging
from django.db import transaction, models
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa, AcaoPdde

logger = logging.getLogger(__name__)


class ExcluirAcaoPDDEException(Exception):
    """Exceção customizada para erros na desabilitação de ações PDDE."""
    pass


class AcoesPddeService:

    def __init__(self, acao: AcaoPdde):
        self.acao = acao

    def _periodo_vigente(self):
        return PeriodoPaa.periodo_vigente()

    def _paas_gerados_e_parciais(self):
        return Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_gerados_e_parciais()

    def _paas_em_elaboracao(self):
        return Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_em_elaboracao()

    def acoes_pdde_receitas_previstas_paas_gerados(self):
        """ Receitas Previstas da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_gerados_e_parciais()

        return self.acao.receitaprevistapdde_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente()
        )

    def acoes_pdde_prioridades_paas_gerados(self):
        """ Prioridades da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_gerados_e_parciais()

        return self.acao.prioridadepaa_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente(),
            acao_pdde=self.acao
        )

    def acoes_pdde_receitas_previstas_paas_elaboracao(self):
        """ Receitas Previstas da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_em_elaboracao()

        return self.acao.receitaprevistapdde_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente()
        )

    def acoes_pdde_prioridades_paas_elaboracao(self):
        """ Prioridades da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_em_elaboracao()

        return self.acao.prioridadepaa_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente(),
            acao_pdde=self.acao
        )

    def excluir_acao_pdde(self):
        # somente este trecho requer transação atomica. Para gerados, é necessário lançar um raise sem invalidar
        # a transação atomica
        with transaction.atomic():
            # verifica se tem elaboração e limpa receitas previstas e o campo acao_pdde das prioridades encontradas
            logger.info('Limpando receitas previstas da ação PDDE em PAAs em elaboração.')
            self.acoes_pdde_receitas_previstas_paas_elaboracao().delete()

            logger.info('Limpando campo de acao_pdde das prioridades da ação PDDE em PAAs em elaboração.')
            self.acoes_pdde_prioridades_paas_elaboracao().update(acao_pdde=None)

        # verifica se tem gerados
        receitas_gerados = self.acoes_pdde_receitas_previstas_paas_gerados().exists()
        prioridades_gerados = self.acoes_pdde_prioridades_paas_gerados().exists()
        if receitas_gerados or prioridades_gerados:
            raise ExcluirAcaoPDDEException(
                ("Esta ação PDDE não pode ser excluída porque está sendo utilizada em "
                 "um Plano Anual de Atividades (PAA).")
            )
