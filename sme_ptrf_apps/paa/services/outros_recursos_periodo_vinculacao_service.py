
from typing import List, Dict, Any
from django.db import transaction
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, Paa
from . import OutroRecursoPeriodoBaseService
import logging

logger = logging.getLogger(__name__)


class UnidadeNaoEncontradaException(Exception):
    """Exceção lançada quando uma unidade não é encontrada."""
    pass


class ValidacaoVinculoException(Exception):
    """Exceção lançada quando uma validação de vínculo falha."""
    pass


class ConfirmacaoVinculoException(Exception):
    """Exceção lançada quando um vínculo necessita de confirmação."""
    pass


class OutroRecursoPeriodoPaaVinculoUnidadeService(OutroRecursoPeriodoBaseService):
    """
    Este service centraliza todas as operações de vínculo, desvínculo de unidades e validações.
    """

    def __init__(self, outro_recurso_periodo: OutroRecursoPeriodoPaa):
        super().__init__(outro_recurso_periodo)

    def _validar_recurso_ativo(self) -> None:
        """
        Valida se o recurso está ativo.

        Raises:
            VinculacaoUnidadeException: Se o recurso estiver inativo
        """
        if not self.outro_recurso_periodo.ativo:
            raise ValidacaoVinculoException(
                "Não é possível vincular unidades a um recurso inativo."
            )

    def _obter_unidade(self, unidade_uuid: str) -> Unidade:
        """
        Obtém uma unidade pelo UUID.

        Args:
            unidade_uuid: UUID da unidade

        Returns:
            Instância da Unidade

        Raises:
            VinculacaoUnidadeException: Se a unidade não for encontrada
        """
        try:
            return Unidade.objects.get(uuid=unidade_uuid)
        except Unidade.DoesNotExist:
            raise UnidadeNaoEncontradaException(
                f"Unidade {unidade_uuid} não encontrada."
            )

    def _obter_unidades(self, unidades_uuid: List[str]) -> List[Unidade]:
        """
        Obtém uma unidade pelo UUID.

        Args:
            unidade_uuid: UUID da unidade

        Returns:
            Instância da Unidade

        Raises:
            VinculacaoUnidadeException: Se a unidade não for encontrada
        """
        return list(Unidade.objects.filter(uuid__in=unidades_uuid))

    def _limpar_registros_da_unidade_no_recurso_em_elaboracao(self, paa: Paa) -> Dict:
        """
        Processa a delimitação para PAA em elaboração.
        Remove o recurso de receitas previstas e prioridades.

        Args:
            paa: Instância do PAA em elaboração

        Returns:
            Dicionário com informações do processamento
        """
        receitas_removidas = self._remover_receitas_previstas_outro_recurso_periodo(paa)
        prioridades_afetadas = self._remover_prioridades_outro_recurso_periodo(paa)

        return {
            'paa_uuid': str(paa.uuid),
            'associacao': paa.associacao.nome if paa.associacao else 'N/A',
            'unidade': str(paa.associacao.unidade.nome) if paa.associacao and paa.associacao.unidade else 'N/A',
            'status': paa.status,
            'receitas_previstas_removidas': receitas_removidas,
            'prioridades_afetadas': prioridades_afetadas,
            'acao': 'Outro Recurso Período removido de receitas previstas e prioridades'
        }

    def obtem_informacao_para_confirmacao(
            self, unidades_a_remover: List[Unidade], verificar_em_paas: List[Paa]) -> Dict:
        """
        Verifica se a delimitação de unidades requer confirmação do usuário.

        Args:
            unidades_a_remover_uuids: Lista de unidades que serão vinculadas

        Returns:
            Dicionário com informações sobre a necessidade de confirmação
        """

        TEXTO_PAAS_EM_ELABORACAO = (
            'As receitas previstas e prioridades serão removidas dos PAA`s que '
            'estão em elaboração. '
        )
        TEXTO_PAAS_GERADO_RETIFICADO = (
            'Existem unidades vinculadas ao período do PAA que utilizaram '
            'o recurso e as demais unidades não poderão ser classificadas '
            'com esse recurso. Caso necessário vincule todas as unidades '
            'ou apenas as unidades necessárias.\n'
        )

        paas_em_elaboracao_encontrados = []
        paas_gerado_retificado_encontrados = []

        for paa in verificar_em_paas:
            if paa.associacao.unidade in unidades_a_remover:

                # Condicionais apenas para contabilizar quando houver em elaboracao/gerado/retificado
                # Essa condicional permitir fomular o texto condicional para exibição em Modal no Usuário
                if self._paa_em_elaboracao(paa):
                    logger.info('Validando paa Em Elaboração: %s', str(paa))

                    # Verifica se o PAA tem receitas previstas e prioridades indicadas
                    tem_receitas = self._receitas_previstas_outro_recurso_periodo_afetadas(paa).exists()
                    logger.info('paa utilizou receitas: %s' % str(tem_receitas))

                    # Verifica se o PAA tem prioridades indicadas
                    tem_prioridades = self._prioridades_afetadas(paa).exists()
                    logger.info('paa utilizou prioridades: %s' % str(tem_prioridades))

                    # Considera PAA em elaboração se tiver receitas ou prioridades indicadas
                    if (tem_receitas or tem_prioridades):
                        paas_em_elaboracao_encontrados.append(paa)

                elif self._paa_retificado(paa):
                    logger.info('Validando paa Em Retificação: %s', str(paa))
                    paas_gerado_retificado_encontrados.append(paa)

                elif self._paa_gerado(paa):
                    logger.info('Validando paa Gerado: %s', str(paa))
                    paas_gerado_retificado_encontrados.append(paa)
                else:
                    pass

        if paas_em_elaboracao_encontrados:
            logs_unidades_em_elaboracao = ', '.join(
                [str(paa.associacao.unidade) for paa in paas_em_elaboracao_encontrados])
            logger.info(f'Unidades com PAA em elaboração encontrados: {logs_unidades_em_elaboracao}')

        if paas_gerado_retificado_encontrados:
            logs_unidades_gerado_retificado = ', '.join(
                [paa.associacao.unidade.codigo_eol for paa in paas_gerado_retificado_encontrados])
            logger.info(f'Unidades com PAA gerado/retificado encontrados: {logs_unidades_gerado_retificado}')

        # Considerando confirmação se houver PAAs em elaboração(com indicação) ou gerado/retificado
        existe_paa_afetado = len(paas_em_elaboracao_encontrados) > 0 or len(paas_gerado_retificado_encontrados) > 0
        if not existe_paa_afetado:
            return {'requer_confirmacao': False, 'mensagem': None}

        info = {
            'requer_confirmacao': existe_paa_afetado,
            'mensagem': ''
        }
        # Se houver PAAs gerado/retificado entrados, exibir primeiramente a seguinte mensagem
        if len(paas_gerado_retificado_encontrados) > 0:
            info['mensagem'] += TEXTO_PAAS_GERADO_RETIFICADO

        # Se houver PAAs em elaboração entrados, acrescentar à mensagem
        if len(paas_em_elaboracao_encontrados) > 0:
            info['mensagem'] += TEXTO_PAAS_EM_ELABORACAO
        return info

    def validar_confirmacao_para_vinculo_unidades(self, unidades_uuid: List[str]) -> None:
        """
        Valida se o recurso necessita de Confirmação para vínculo de unidades
        Considerando que o Recurso tem todas as unidades vinculadas, inicialmente
        """
        unidades = self._obter_unidades(unidades_uuid)
        unidades_atuais = list(self.outro_recurso_periodo.unidades.all())

        # Esta lista pode incluir unidade que já possuia vinculo quando TODAS estava habilitada
        unidades_atualizadas = unidades_atuais + unidades

        # Valida se o recurso estava disponível para todas as unidades
        if self._tinha_todas_unidades():

            paas_afetados_em_elaboracao = list(self._paas_afetados_em_elaboracao())
            paas_afetados_gerado_retificacao = list(self._paas_afetados_gerado_retificado())

            paas_afetados = paas_afetados_em_elaboracao + paas_afetados_gerado_retificacao
            # Obter info de unidades exceto as unidades atualizadas
            unidades_a_verificar = [
                paa.associacao.unidade
                for paa in paas_afetados
                if paa.associacao.unidade not in unidades_atualizadas
            ]

            info = self.obtem_informacao_para_confirmacao(unidades_a_verificar, paas_afetados)
            logger.info(info)
            if info['requer_confirmacao']:
                raise ConfirmacaoVinculoException(info['mensagem'])

    def validar_confirmacao_para_desvinculo_unidades(self, unidades_a_remover_uuids: List[str]) -> None:
        """
        Valida se o recurso necessita de Confirmação para desvínculo de unidades
        Considerando que pode haver unidades em desvínculo com registros de receitas/prioridades
        """
        unidades_a_remover = self._obter_unidades(unidades_a_remover_uuids)
        paas_afetados_em_elaboracao = list(self._paas_afetados_em_elaboracao())
        paas_afetados_gerado_retificacao = list(self._paas_afetados_gerado_retificado())
        paas_afetados = paas_afetados_em_elaboracao + paas_afetados_gerado_retificacao

        # Obter info de unidades que utilizaram o recurso
        info = self.obtem_informacao_para_confirmacao(unidades_a_remover, paas_afetados)
        if info['requer_confirmacao']:
            raise ConfirmacaoVinculoException(info['mensagem'])

    @transaction.atomic
    def vincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Vincula todas as unidades.

        Não valida se o recurso precisa de confirmação para vinculo
        Apenas habilita para todas as unidades

        Returns:
            Dicionário com status da operação

        """

        unidades = list(self.outro_recurso_periodo.unidades.all())

        if not unidades:
            return {
                'sucesso': True,
                'mensagem': 'Todas as Unidades já estão habilitadas no Recurso.',
            }

        # Remove todas as unidades
        self.outro_recurso_periodo.unidades.clear()

        logger.warning(
            f"Todas as Unidades foram habilitadas no "
            f"recurso {self.outro_recurso_periodo.outro_recurso.nome} no período "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )

        return {
            'sucesso': True,
            'mensagem': 'Todas as unidades foram habilitadas com sucesso!',
        }

    @transaction.atomic
    def vincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Vincula as unidades ao recurso.

        Parameters:
        unidades_uuid (List[str]): lista de UUIDs das unidades a serem vinculadas

        Returns:
            Dicionário com status da operação
        """
        unidades = self._obter_unidades(unidades_uuid)

        if not unidades:
            raise ValidacaoVinculoException(
                'Nenhuma unidade foi identificada para vínculo.',
            )

        unidades_atuais = list(self.outro_recurso_periodo.unidades.all())

        # Esta lista pode incluir unidade que já possuia vinculo quando TODAS estava habilitada
        unidades_atualizadas = unidades_atuais + unidades

        # Valida se o recurso está ativo
        self._validar_recurso_ativo()

        paas_processados = []
        # Valida se o recurso estava disponível para todas as unidades
        if self._tinha_todas_unidades():
            paas_afetados_em_elaboracao = self._paas_afetados_em_elaboracao()

            # Processar PAAs afetados em elaboração
            for paa in paas_afetados_em_elaboracao:
                if paa.associacao.unidade not in unidades_atualizadas:
                    logger.info(f"Processando PAA {str(paa)} com remoção de receitas e prioridades")
                    # Se Unidade do PAA não estiver na lista das novas unidades, aplicar regras de vínculos
                    info = self._limpar_registros_da_unidade_no_recurso_em_elaboracao(paa)
                    paas_processados.append(info)

        # Vincular a nova unidade
        # mantem as unidades com PAA Gerado/Retificacao que tenham receitas/prioridades do respectivo Outro Recurso
        paas = self._paas_afetados_gerado_retificado()
        unidades_paa_gerado_retificado_com_receitas_prioridades = []
        for paa in paas:
            receitas = self._receitas_previstas_outro_recurso_periodo_afetadas(paa).exists()
            prioridades = self._prioridades_afetadas(paa).exists()
            if receitas or prioridades:
                unidades_paa_gerado_retificado_com_receitas_prioridades.append(paa.associacao.unidade)

        logger.info((
            "Mantendo Unidades com PAA Gerado/Retificacao ao vincular: "
            f"{str(unidades_paa_gerado_retificado_com_receitas_prioridades)}"))
        unidades_atualizadas += unidades_paa_gerado_retificado_com_receitas_prioridades

        self.outro_recurso_periodo.unidades.set(unidades_atualizadas)

        log_unidades = ', '.join([str(unidade) for unidade in unidades])
        logger.info(
            f"Unidades {log_unidades} vinculadas ao "
            f"recurso {self.outro_recurso_periodo.outro_recurso.nome} no operíodo "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )
        logger.info(
            f"PAAs afetados com remoção de receitas e prioridades: {str(paas_processados)}"
        )

        return {
            'sucesso': True,
            'mensagem': (
                'Unidades vinculadas com sucesso!'
                if len(unidades) > 1
                else 'Unidade vinculada com sucesso!'),
            'unidade': str(log_unidades),
            'ja_vinculada': False
        }

    @transaction.atomic
    def desvincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Desvincula as unidades do recurso.

        Parameters:
        unidades_uuid (List[str]): lista de UUIDs das unidades a serem desvinculadas

        Returns:
            Dicionário com status da operação
        """
        unidades = self._obter_unidades(unidades_uuid)

        if not unidades:
            raise ValidacaoVinculoException(
                'Nenhuma unidade foi identificada para desvínculo.',
            )

        logger.info(f"Unidades a serem desvinculadas: {str([str(u) for u in unidades])}")

        # Valida se o recurso está ativo
        self._validar_recurso_ativo()

        paas_processados = []

        # Processar PAAs em elaboração
        for paa in self._paas_afetados_em_elaboracao():
            logger.info('Verificando PAA afetado %s' % str(paa))
            # Para o desvínculo, a lógica aqui é inversa em relação ao vínculo
            if paa.associacao.unidade in unidades:
                logger.info('Limpando a receitas e prioridades indicadas para o PAA %s' % str(paa))
                # Limpar registros do próprio PAA da unidade
                info = self._limpar_registros_da_unidade_no_recurso_em_elaboracao(paa)
                paas_processados.append(info)

        # desvincular as unidades (filtra todas atuais, exceto as unidades a desvincular)
        unidades_atualizadas = list(self.outro_recurso_periodo.unidades.exclude(uuid__in=unidades_uuid))
        logger.info(f"Unidades atualizadas no Outro Recurso Período: {str([str(u) for u in unidades_atualizadas])}")

        # mantem as unidades com PAA Gerado/Retificacao
        # mantem as unidades com PAA Gerado/Retificacao que tenham receitas/prioridades do respectivo Outro Recurso
        paas = self._paas_afetados_gerado_retificado()
        unidades_paa_gerado_retificado_com_receitas_prioridades = []
        for paa in paas:
            receitas = self._receitas_previstas_outro_recurso_periodo_afetadas(paa).exists()
            prioridades = self._prioridades_afetadas(paa).exists()
            if receitas or prioridades:
                unidades_paa_gerado_retificado_com_receitas_prioridades.append(paa.associacao.unidade)

        logger.info((
            "Mantendo Unidades com PAA Gerado/Retificacao ao desvincular: "
            f"{str(unidades_paa_gerado_retificado_com_receitas_prioridades)}"))
        unidades_atualizadas += unidades_paa_gerado_retificado_com_receitas_prioridades
        if unidades_atualizadas:
            # verifica se está parcial, para incluir a unidade com PAA GERADO/RETIFICACAO
            unidades_atualizadas += unidades_paa_gerado_retificado_com_receitas_prioridades

        # define as unidades atualizadas
        self.outro_recurso_periodo.unidades.set(unidades_atualizadas)

        logs_unidades = ', '.join([str(unidade) for unidade in unidades])
        logger.info(
            f"Unidades {logs_unidades} desvinculadas do "
            f"recurso {self.outro_recurso_periodo.outro_recurso.nome} no operíodo "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )
        logger.info(
            f"PAAs afetados com remoção de receitas e prioridades: {str(paas_processados)}"
        )

        return {
            'sucesso': True,
            'mensagem': (
                'Unidades desvinculadas com sucesso!'
                if len(unidades_uuid) > 1
                else 'Unidade desvinculada com sucesso!'
            ),
            'unidade': str(logs_unidades),
            'ja_vinculada': False
        }
