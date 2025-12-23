
from typing import List, Dict, Any, Optional, Tuple
from django.db import transaction
from django.db.models import Q
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa, PeriodoPaa
from sme_ptrf_apps.paa.api.serializers.outros_recursos_periodo_paa_serializer import OutrosRecursosPeriodoPaaSerializer
import logging

logger = logging.getLogger(__name__)


class ImportacaoUnidadesOutroRecursoException(Exception):
    """Exceção lançada quando ocorre erro na importação de unidades."""


class VinculoUnidadeException(Exception):
    """Exceção base para erros de vínculo de unidades."""
    pass


class UnidadeNaoEncontradaException(VinculoUnidadeException):
    """Exceção lançada quando uma unidade não é encontrada."""
    pass


class ValidacaoVinculoException(VinculoUnidadeException):
    """Exceção lançada quando uma validação de vínculo falha."""
    pass


class OutroRecursoPeriodoPaaUnidadeService:
    """
    Este service centraliza todas as operações de vínculo, desvínculo de unidades e validações.
    """

    def __init__(self, outro_recurso_periodo: OutroRecursoPeriodoPaa):
        """
        Inicializa o service com uma instância de OutroRecursoPeriodoPaa.

        Args:
            outro_recurso_periodo: Instância do modelo OutroRecursoPeriodoPaa
        """
        self.outro_recurso_periodo = outro_recurso_periodo

    # ==================== VALIDAÇÕES ====================

    def _validar_pode_vincular(self, unidades: List[Unidade]) -> Tuple[bool, Optional[str]]:
        """
        Valida se as unidades podem ser vinculadas ao período.

        Este método pode ser expandido para incluir validações como:
        - Verificar se o período está ativo
        - Verificar se as unidades já possuem outros vínculos conflitantes
        - Verificar regras de negócio específicas
        - Validar hierarquia DRE/Unidade

        Args:
            unidades: Lista de unidades a serem vinculadas

        Returns:
            Tupla (sucesso, mensagem_erro)
        """
        # Validação: período deve estar ativo
        if not self.outro_recurso_periodo.ativo:
            return False, "Não é possível vincular unidades a um período inativo."

        # Exemplo: verificar status de PAA
        # if self._paa_gerado(paa):
        #     return False, "Não é possível vincular unidades pois o PAA já foi gerado."

        return True, None

    def _validar_pode_desvincular(self, unidades: List[Unidade]) -> Tuple[bool, Optional[str]]:
        """
        Valida se as unidades podem ser desvinculadas do período.

        Este método pode incluir validações como:
        - Verificar se existem PAAs criados para as unidades
        - Outras validações para desvínculo

        Args:
            unidades: Lista de unidades a serem desvinculadas

        Returns:
            Tupla (sucesso, mensagem_erro)
        """

        # Exemplo: verificar PCS
        # if self._possui_pcs_abertas(unidades):
        #     return False, "Existem PCs em aberto para estas unidades."

        return True, None

    # ==================== OPERAÇÕES DE VÍNCULO ====================

    @transaction.atomic
    def vincular_unidade(self, unidade_uuid: str) -> Dict[str, Any]:
        """
        Vincula uma única unidade ao período.

        Args:
            unidade_uuid: UUID da unidade a ser vinculada

        Returns:
            Dicionário com status da operação

        Raises:
            UnidadeNaoEncontradaException: Se a unidade não for encontrada
            ValidacaoVinculoException: Se a validação falhar
        """
        try:
            unidade = Unidade.objects.select_related('dre').get(uuid=unidade_uuid)
        except Unidade.DoesNotExist:
            logger.error(f"Tentativa de vincular unidade inexistente: {unidade_uuid}")
            raise UnidadeNaoEncontradaException("Unidade não encontrada.")

        # # Verifica se já está vinculada
        if self.outro_recurso_periodo.unidades.filter(uuid=unidade_uuid).exists():
            return {
                'sucesso': True,
                'mensagem': 'Unidade já estava vinculada ao período.',
                'unidade': str(unidade),
                'ja_vinculada': True
            }

        # Valida o vínculo
        pode_vincular, mensagem_erro = self._validar_pode_vincular([unidade])
        if not pode_vincular:
            logger.warning(f"Validação falhou ao vincular unidade {unidade_uuid}: {mensagem_erro}")
            raise ValidacaoVinculoException(mensagem_erro)

        # Realiza o vínculo
        self.outro_recurso_periodo.unidades.add(unidade)

        logger.info(
            f"Unidade {unidade.codigo_eol} vinculada ao "
            f"recurso {self.outro_recurso_periodo.outro_recurso.nome} no operíodo "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )

        return {
            'sucesso': True,
            'mensagem': 'Unidade vinculada com sucesso!',
            'unidade': str(unidade),
            'ja_vinculada': False
        }

    @transaction.atomic
    def vincular_unidades_em_lote(self, unidade_uuids: List[str]) -> Dict[str, Any]:
        """
        Vincula múltiplas unidades ao período em uma única transação.

        Args:
            unidade_uuids: Lista de UUIDs das unidades

        Returns:
            Dicionário com detalhes da operação

        Raises:
            ValidacaoVinculoException: Se a validação falhar
        """
        if not unidade_uuids:
            raise ValidacaoVinculoException("Nenhuma unidade foi informada.")

        # Busca todas as unidades
        unidades = list(
            Unidade.objects.select_related('dre')
            .filter(uuid__in=unidade_uuids)
        )

        if not unidades:
            raise UnidadeNaoEncontradaException("Nenhuma unidade válida foi encontrada.")

        # Identifica unidades já vinculadas
        unidades_vinculadas = set(
            self.outro_recurso_periodo.unidades
            .filter(uuid__in=unidade_uuids)
            .values_list('uuid', flat=True)
        )

        unidades_para_vincular = [
            u for u in unidades if str(u.uuid) not in unidades_vinculadas
        ]

        if not unidades_para_vincular:
            return {
                'sucesso': True,
                'mensagem': 'Todas as unidades já estavam vinculadas.',
                'total_solicitado': len(unidade_uuids),
                'total_vinculado': 0,
                'total_ja_vinculado': len(unidades_vinculadas)
            }

        # Valida o vínculo
        pode_vincular, mensagem_erro = self._validar_pode_vincular(unidades_para_vincular)
        if not pode_vincular:
            logger.warning(f"Validação falhou ao vincular lote: {mensagem_erro}")
            raise ValidacaoVinculoException(mensagem_erro)

        # Realiza o vínculo em lote
        self.outro_recurso_periodo.unidades.add(*unidades_para_vincular)

        logger.info(
            f"{len(unidades_para_vincular)} unidades vinculadas "
            f"ao recurso {self.outro_recurso_periodo.outro_recurso.nome} no período "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )

        return {
            'sucesso': True,
            'mensagem': 'Unidades vinculadas com sucesso!',
            'total_solicitado': len(unidade_uuids),
            'total_vinculado': len(unidades_para_vincular),
            'total_ja_vinculado': len(unidades_vinculadas),
            'unidades_vinculadas': [u.codigo_eol for u in unidades_para_vincular]
        }

    # ==================== OPERAÇÕES DE DESVÍNCULO ====================

    @transaction.atomic
    def desvincular_unidade(self, unidade_uuid: str) -> Dict[str, Any]:
        """
        Desvincula uma única unidade do período.

        Args:
            unidade_uuid: UUID da unidade a ser desvinculada

        Returns:
            Dicionário com status da operação

        Raises:
            UnidadeNaoEncontradaException: Se a unidade não estiver vinculada
            ValidacaoVinculoException: Se a validação falhar
        """
        try:
            unidade = self.outro_recurso_periodo.unidades.get(uuid=unidade_uuid)
        except Unidade.DoesNotExist:
            logger.error(f"Tentativa de desvincular unidade não vinculada: {unidade_uuid}")
            raise UnidadeNaoEncontradaException(
                "Unidade não encontrada ou já desvinculada."
            )

        # Valida o desvínculo
        pode_desvincular, mensagem_erro = self._validar_pode_desvincular([unidade])
        if not pode_desvincular:
            logger.warning(f"Validação falhou ao desvincular unidade {unidade_uuid}: {mensagem_erro}")
            raise ValidacaoVinculoException(mensagem_erro)

        # Realiza o desvínculo
        self.outro_recurso_periodo.unidades.remove(unidade)

        logger.info(
            f"Unidade {unidade.codigo_eol} desvinculada do "
            f"recurso {self.outro_recurso_periodo.outro_recurso.nome} no período "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )

        return {
            'sucesso': True,
            'mensagem': 'Unidade desvinculada com sucesso!',
            'unidade': str(unidade)
        }

    @transaction.atomic
    def desvincular_unidades_em_lote(self, unidade_uuids: List[str]) -> Dict[str, Any]:
        """
        Desvincula múltiplas unidades do período em uma única transação.
        Args:
            unidade_uuids: Lista de UUIDs das unidades

        Returns:
            Dicionário com detalhes da operação

        Raises:
            ValidacaoVinculoException: Se a validação falhar
        """
        if not unidade_uuids:
            raise ValidacaoVinculoException("Nenhuma unidade foi informada.")

        # Busca unidades vinculadas
        unidades = list(
            self.outro_recurso_periodo.unidades
            .select_related('dre')
            .filter(uuid__in=unidade_uuids)
        )

        if not unidades:
            raise UnidadeNaoEncontradaException(
                "Nenhuma unidade encontrada ou já desvinculada."
            )

        # Valida o desvínculo
        pode_desvincular, mensagem_erro = self._validar_pode_desvincular(unidades)
        if not pode_desvincular:
            logger.warning(f"Validação falhou ao desvincular lote: {mensagem_erro}")
            raise ValidacaoVinculoException(mensagem_erro)

        # Realiza o desvínculo em lote
        self.outro_recurso_periodo.unidades.remove(*unidades)

        logger.info(
            f"{len(unidades)} unidades desvinculadas do período "
            f"{self.outro_recurso_periodo.periodo_paa.referencia}"
        )

        return {
            'sucesso': True,
            'mensagem': 'Unidades desvinculadas com sucesso!',
            'total_desvinculado': len(unidades),
            'unidades_desvinculadas': [u.codigo_eol for u in unidades]
        }

    @transaction.atomic
    def vincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Vincula todas as unidades.

        Returns:
            Dicionário com status da operação

        Raises:
            ValidacaoVinculoException: Se a validação falhar
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


class OutroRecursoPeriodoPaaService:

    @classmethod
    def importar_unidades(cls, destino: OutroRecursoPeriodoPaa, origem_uuid: str):
        if not origem_uuid:
            raise ImportacaoUnidadesOutroRecursoException(
                "origem_uuid é obrigatório."
            )

        origem = cls._obter_origem(origem_uuid)

        cls._validar_origem_destino(destino, origem)

        with transaction.atomic():
            cls._executar_importacao(destino, origem)

    @classmethod
    def _obter_origem(cls, origem_uuid: str) -> OutroRecursoPeriodoPaa:
        try:
            return OutroRecursoPeriodoPaa.objects.prefetch_related(
                'unidades'
            ).get(uuid=origem_uuid)
        except OutroRecursoPeriodoPaa.DoesNotExist:
            raise ImportacaoUnidadesOutroRecursoException(
                "Recurso de origem não encontrado."
            )

    @classmethod
    def _validar_origem_destino(cls, destino, origem):
        if destino.uuid == origem.uuid:
            raise ImportacaoUnidadesOutroRecursoException(
                "O recurso de origem não pode ser o mesmo que o destino."
            )

    @classmethod
    def _executar_importacao(cls, destino, origem):
        unidades = origem.unidades.all()

        if not unidades.exists():
            return

        destino.unidades.add(*unidades)


class OutroRecursoPeriodoPaaListagemService:
    def __init__(self, periodo_paa: PeriodoPaa, unidade: Unidade):
        self.periodo_paa = periodo_paa
        self.unidade = unidade

    def queryset_listar_outros_recursos_periodo_unidade(self):
        """
        Retorna uma lista de recursos vinculados ao Período do PAA,
        filtrados por período, ativo e vinculados a uma unidade.
        A lista é ordenada por nome do recurso.
        """
        return OutroRecursoPeriodoPaa.objects.filter(
            periodo_paa=self.periodo_paa,
            ativo=True,
        ).filter(
            Q(unidades__in=[self.unidade]) | Q(unidades__isnull=True)
        ).distinct().order_by('outro_recurso__nome')

    def serialized_listar_outros_recursos_periodo_unidade(self):
        """
        Retorna a lista serializada de recursos vinculados ao PAA,
        filtrados por período, ativo e vinculados a uma unidade.
        A lista é ordenada por nome do recurso.
        """
        qs = self.queryset_listar_outros_recursos_periodo_unidade()

        serializer = OutrosRecursosPeriodoPaaSerializer(qs, many=True)

        return serializer.data
