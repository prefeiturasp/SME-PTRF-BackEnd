import logging
from django.db import transaction
from typing import List, Dict, Any
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.despesas.models import TipoCusteio

logger = logging.getLogger(__name__)


class ValidacaoVinculoException(Exception):
    """Exceção lançada quando uma validação de vínculo falha."""
    pass


class UnidadeNaoEncontradaException(Exception):
    """Exceção lançada quando uma unidade não é encontrada."""
    pass


class TipoCusteioVinculoUnidadeService:

    """
    Este service centraliza todas as operações de vínculo, desvínculo de unidades e validações.
    """

    def __init__(self, tipo_custeio: TipoCusteio):
        self.tipo_custeio = tipo_custeio

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

    @transaction.atomic
    def vincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Vincula todas as unidades.

        Não valida se o tipo Custeio precisa de confirmação para vinculo
        Apenas habilita para todas as unidades

        Returns:
            Dicionário com status da operação

        """

        unidades = list(self.tipo_custeio.unidades.all())

        if not unidades:
            return {
                'sucesso': True,
                'mensagem': 'Todas as Unidades já estão habilitadas no Tipo Custeio.',
            }

        # Remove todas as unidades
        self.tipo_custeio.unidades.clear()

        logger.warning("Todas as Unidades foram habilitadas no Tipo Custeio.")

        return {
            'sucesso': True,
            'mensagem': 'Todas as unidades foram habilitadas com sucesso!',
        }

    @transaction.atomic
    def desvincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Desvincula as unidades do tipo custeio.

        Parameters:
            unidades_uuid (List[str]): lista de UUIDs das unidades a serem desvinculadas

        Returns:
            Dict[str, Any]: status da operação
        """
        unidades = self._obter_unidades(unidades_uuid)

        if not unidades:
            raise ValidacaoVinculoException('Nenhuma unidade foi identificada para desvínculo.', )

        qt_nao_removidas = 0

        for unidade in unidades:
            possui_receitas = self.tipo_custeio.receita_set.filter(
                associacao__unidade=unidade
            ).exists()

            if possui_receitas:
                qt_nao_removidas += 1
                continue

            self.tipo_custeio.unidades.remove(unidade)

        if qt_nao_removidas == len(unidades):
            raise ValidacaoVinculoException(
                "Não é possível restringir o tipo de crédito, pois "
                "existem unidades que já possuem crédito criado com esse "
                "tipo e não estão selecionadas."
            )

        mensagem_retorno = (
            "Unidades desvinculadas com sucesso!"
            if len(unidades) > 1
            else "Unidade desvinculada com sucesso!"
        )

        return {
            "sucesso": True,
            "mensagem": mensagem_retorno,
        }
