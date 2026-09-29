import logging

from django.db.models import Prefetch
from django.db import transaction, models
from sme_ptrf_apps.paa.services.acoes_paa_service import AcoesPaaService
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa, AcaoPdde

logger = logging.getLogger(__name__)


class ExcluirAcaoPDDEException(Exception):
    """Exceção customizada para erros na desabilitação de ações PDDE."""
    pass


class AcoesPddeService:

    def __init__(self, acao: AcaoPdde) -> None:
        """Inicializa o service com a instância da ação PDDE."""
        self.acao = acao

    def _periodo_vigente(self) -> PeriodoPaa:
        """Retorna o período PAA vigente."""
        return PeriodoPaa.periodo_vigente()

    def _paas_gerados_e_parciais(self) -> models.QuerySet:
        """Retorna subquery de PAAs gerados ou gerados parcialmente."""
        return Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_gerados_e_parciais()

    def _paas_em_elaboracao(self) -> models.QuerySet:
        """Retorna subquery de PAAs em elaboração."""
        return Paa.objects.filter(
            pk=models.OuterRef('paa_id')).paas_em_elaboracao()

    def acoes_pdde_receitas_previstas_paas_gerados(self) -> models.QuerySet:
        """ Receitas Previstas da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_gerados_e_parciais()

        return self.acao.receitaprevistapdde_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente()
        )

    def acoes_pdde_prioridades_paas_gerados(self) -> models.QuerySet:
        """ Prioridades da Ação PDDE em PAAs Gerados/Gerados Parcialmente """
        paas_andamento = self._paas_gerados_e_parciais()

        return self.acao.prioridadepaa_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente(),
            acao_pdde=self.acao
        )

    def acoes_pdde_receitas_previstas_paas_elaboracao(self) -> models.QuerySet:
        """ Receitas Previstas da Ação PDDE em PAAs em Elaboração """
        paas_andamento = self._paas_em_elaboracao()

        return self.acao.receitaprevistapdde_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente()
        )

    def acoes_pdde_prioridades_paas_elaboracao(self) -> models.QuerySet:
        """ Prioridades da Ação PDDE em PAAs em Elaboração """
        paas_andamento = self._paas_em_elaboracao()

        return self.acao.prioridadepaa_set.filter(
            models.Exists(paas_andamento),
            paa__periodo_paa=self._periodo_vigente(),
            acao_pdde=self.acao
        )

    def excluir_acao_pdde(self) -> None:
        """Remove a ação PDDE limpando receitas e prioridades em PAAs em elaboração."""
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


class ResumoAcoesPddeService:
    """
    Monta a estrutura hierárquica de Ações PDDE agrupadas por Programa,
    pronta para renderização direta na tabela do frontend (Programa > Ações + Total do PDDE).
    """

    def __init__(self, paa: Paa) -> None:
        self.paa: Paa = paa

    def _obter_acoes_com_receitas(self):
        """Retorna as Ações PDDE do PAA com a receita prevista já carregada (evita N+1). Somente do paa específico"""
        from sme_ptrf_apps.paa.models import ReceitaPrevistaPdde

        receitas_do_paa = ReceitaPrevistaPdde.objects.filter(paa=self.paa)
        return (
            AcoesPaaService(self.paa)
            .obter_pdde()
            .select_related('programa')
            .prefetch_related(
                Prefetch('receitaprevistapdde_set', queryset=receitas_do_paa, to_attr='receita_prevista_paa')
            )
        )

    def _serializar_receita(self, acao: AcaoPdde) -> dict | None:
        """
        Serializa a receita prevista da ação, no formato que o Modal de edição já espera.

        Args:
            acao (AcaoPdde): Ação PDDE com a receita prevista pré-carregada via prefetch

        Returns:
            dict | None: Valores de previsão e saldo da receita, ou None se não houver receita
        """
        receita = acao.receita_prevista_paa[0] if acao.receita_prevista_paa else None
        if not receita:
            return None

        return {
            'uuid': str(receita.uuid),
            'previsao_valor_custeio': float(receita.previsao_valor_custeio),
            'previsao_valor_capital': float(receita.previsao_valor_capital),
            'previsao_valor_livre': float(receita.previsao_valor_livre),
            'saldo_custeio': float(receita.saldo_custeio),
            'saldo_capital': float(receita.saldo_capital),
            'saldo_livre': float(receita.saldo_livre),
        }

    def _node_acao(self, acao: AcaoPdde) -> dict:
        """
        Monta o node da ação PDDE com os totais de custeio, capital e livre aplicação.

        Args:
            acao (AcaoPdde): Ação PDDE com a receita prevista pré-carregada via prefetch

        Returns:
            dict: Node da ação pronto para renderização na tabela do frontend
        """
        PREFIXO_ACAO = 'PDDE'
        receita = self._serializar_receita(acao)
        custeio = (receita['previsao_valor_custeio'] + receita['saldo_custeio']) if receita else 0
        capital = (receita['previsao_valor_capital'] + receita['saldo_capital']) if receita else 0
        livre = (receita['previsao_valor_livre'] + receita['saldo_livre']) if receita else 0

        return {
            'key': str(acao.uuid),
            'nome': f'{PREFIXO_ACAO} {acao.nome}',
            'level': 1,
            'aceita_custeio': acao.aceita_custeio,
            'aceita_capital': acao.aceita_capital,
            'aceita_livre_aplicacao': acao.aceita_livre_aplicacao,
            'custeio': custeio,
            'capital': capital,
            'livre_aplicacao': livre,
            'acao': {
                'uuid': str(acao.uuid),
                'nome': acao.nome,
                'aceita_custeio': acao.aceita_custeio,
                'aceita_capital': acao.aceita_capital,
                'aceita_livre_aplicacao': acao.aceita_livre_aplicacao,
                'receitas_previstas_pdde_valores': receita,
            },
        }

    def resumo_por_programa(self) -> list:
        """Retorna a lista de nodes: um por Programa (com filhas Ações) + o node 'Total do PDDE'."""
        PREFIXO_PROGRAMA = 'PDDE'
        SUFIXO_PROGRAMA = 'Total'
        programas_map = {}
        totais_gerais = {'custeio': 0, 'capital': 0, 'livre_aplicacao': 0}

        for acao in self._obter_acoes_com_receitas():
            if acao.programa is None:
                continue

            node_acao = self._node_acao(acao)

            node_programa = programas_map.setdefault(acao.programa.uuid, {
                'key': str(acao.programa.uuid),
                'nome': f'{PREFIXO_PROGRAMA} {acao.programa.nome} {SUFIXO_PROGRAMA}',
                'level': 0,
                'custeio': 0,
                'capital': 0,
                'livre_aplicacao': 0,
                'children': [],
            })

            node_programa['children'].append(node_acao)
            node_programa['custeio'] += node_acao['custeio']
            node_programa['capital'] += node_acao['capital']
            node_programa['livre_aplicacao'] += node_acao['livre_aplicacao']

            totais_gerais['custeio'] += node_acao['custeio']
            totais_gerais['capital'] += node_acao['capital']
            totais_gerais['livre_aplicacao'] += node_acao['livre_aplicacao']

        dados = list(programas_map.values())
        dados.append({
            'key': 'total-pdde',
            'nome': 'Total do PDDE',
            'level': 0,
            'custeio': totais_gerais['custeio'],
            'capital': totais_gerais['capital'],
            'livre_aplicacao': totais_gerais['livre_aplicacao'],
        })
        return dados
