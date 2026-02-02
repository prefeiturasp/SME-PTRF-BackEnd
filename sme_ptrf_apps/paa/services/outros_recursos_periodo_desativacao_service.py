
from typing import Dict
from django.db import transaction
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, Paa
from . import OutroRecursoPeriodoBaseService
import logging

logger = logging.getLogger(__name__)


class DesabilitacaoRecursoException(Exception):
    """Exceção customizada para erros na desabilitação de recursos."""
    pass


class OutroRecursoPeriodoDesabilitacaoService(OutroRecursoPeriodoBaseService):

    def __init__(self, outro_recurso_periodo: OutroRecursoPeriodoPaa):
        super().__init__(outro_recurso_periodo)

    def aplica_regras_desabilitacao_em_elaboracao(self, paa: Paa) -> Dict:
        """
        Processa a desabilitação do recurso para PAA em elaboração.

        Args:
            paa: Instância do PAA em elaboração

        Returns:
            Dicionário com informações do processamento
        """
        receitas_removidas = self._remover_receitas_previstas_outro_recurso_periodo(paa)
        prioridades_afetadas = self._remover_prioridades_outro_recurso_periodo(paa)

        return {
            'paa_uuid': str(paa.uuid),
            'associacao': str(paa.associacao.unidade) if paa.associacao else 'N/A',
            'status': paa.status,
            'receitas_previstas': receitas_removidas,
            'prioridades_afetadas': prioridades_afetadas,
            'acao': 'Recurso removido de receitas previstas e prioridades'
        }

    def aplica_regras_desabilitacao_gerado_retificacao(self, paa: Paa) -> Dict:
        """
        Processa a desabilitação do recurso para PAA gerado ou em retificação.

        Args:
            paa: Instância do PAA gerado ou em retificação

        Returns:
            Dicionário com informações do processamento
        """
        return {
            'paa_uuid': str(paa.uuid),
            'associacao': str(paa.associacao.unidade) if paa.associacao else 'N/A',
            'status': paa.status,
            'acao': 'Recurso mantido em receitas previstas e prioridades'
        }

    @transaction.atomic
    def desabilitar_outro_recurso_periodo(self) -> Dict:
        """
        Desabilita o recurso aplicando as regras de negócio conforme o status dos PAAs.

        Returns:
            Dicionário com o resultado da operação

        Raises:
            DesabilitacaoRecursoException: Em caso de erro na desabilitação
        """
        if not self._outro_recurso_periodo_ativo():
            raise DesabilitacaoRecursoException("O recurso já está desabilitado.")

        paas_afetados = self._obtem_paas_afetados()

        resultado = {
            'sucesso': True,
            'mensagem': 'Recurso desabilitado com sucesso.',
            'recurso': str(self.outro_recurso_periodo.outro_recurso),
            'periodo': str(self.outro_recurso_periodo.periodo_paa),
            'total_paas': len(paas_afetados),
            'paas_processados': []
        }

        try:

            # Processar cada PAA de acordo com seu status
            for paa in paas_afetados:
                if self._paa_em_elaboracao(paa):
                    info = self.aplica_regras_desabilitacao_em_elaboracao(paa)
                elif self._paa_gerado_retificado(paa):
                    info = self.aplica_regras_desabilitacao_gerado_retificacao(paa)
                else:
                    info = {
                        'paa_uuid': str(paa.uuid),
                        'associacao': str(paa.associacao.unidade) if paa.associacao else 'N/A',
                        'status': paa.status,
                        'acao': 'Status não tratado'
                    }
                    logger.info(str(info))
                resultado['paas_processados'].append(info)

            # Ao habilitar o recurso, ele torna-se disponível para todas as unidades
            self.outro_recurso_periodo.unidades.clear()
            # Desabilitar o recurso
            self.outro_recurso_periodo.ativo = False
            self.outro_recurso_periodo.save()

            logger.info(
                f"Recurso {self.outro_recurso_periodo.outro_recurso.nome} desabilitado com sucesso. "
                f"Total de PAAs processados: {len(paas_afetados)}"
            )

            return resultado

        except Exception as e:
            logger.error(
                f"Erro ao desabilitar recurso {self.outro_recurso_periodo.uuid}: {str(e)}",
                exc_info=True
            )
            raise DesabilitacaoRecursoException(f"Erro ao desabilitar recurso: {str(e)}")

    def obter_informacoes_para_confirmacao(self) -> Dict:
        """
        Obtém informações prévias do impacto da desativação do recurso.

        Returns:
            Dicionário com informações para a modal
        """
        paas_afetados = self._obtem_paas_afetados()

        paas_em_elaboracao = [
            paa for paa in paas_afetados
            if self._paa_em_elaboracao(paa)
        ]

        paas_gerados = [
            paa for paa in paas_afetados
            if self._paa_gerado_retificado(paa)
        ]

        return {
            'recurso': str(self.outro_recurso_periodo.outro_recurso),
            'periodo': str(self.outro_recurso_periodo.periodo_paa),
            'total_paas': len(paas_afetados),
            'paas_em_elaboracao': len(paas_em_elaboracao),
            'paas_gerados_ou_retificacao': len(paas_gerados),
            'detalhes': {
                'em_elaboracao': [
                    {
                        'uuid': str(paa.uuid),
                        'associacao': str(paa.associacao.unidade) if paa.associacao else 'N/A',
                        'receitas_previstas': len(self._receitas_previstas_outro_recurso_periodo_afetadas(paa)),
                        'prioridades': len(self._prioridades_afetadas(paa)),
                    } for paa in paas_em_elaboracao
                ],
                'gerados_ou_retificacao': [
                    {
                        'uuid': str(paa.uuid),
                        'associacao': str(paa.associacao.unidade) if paa.associacao else 'N/A',
                        'receitas_previstas': len(self._receitas_previstas_outro_recurso_periodo_afetadas(paa)),
                        'prioridades': len(self._prioridades_afetadas(paa)),
                    } for paa in paas_gerados
                ]
            }
        }
