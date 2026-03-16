import logging
from django.db import transaction
from django.db.models.query_utils import Q
from typing import List, Dict, Any
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.despesas.models import TipoCusteio
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_COMPLETO, STATUS_INCOMPLETO

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
    def vincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Vincula as unidades do tipo de custeio.

        Parameters:
            unidades_uuid (List[str]): lista de UUIDs das unidades a serem vinculadas

        Returns:
            Dict[str, Any]: status da operação
        """
        
        unidades = self._obter_unidades(unidades_uuid)

        if not unidades_uuid or not unidades:
            raise ValidacaoVinculoException(
                "Nenhuma unidade foi identificada para desvínculo."
            )

               
        self.tipo_custeio.unidades.add(*unidades)

        mensagem = (
            "Unidades desvinculadas com sucesso!"
            if len(unidades) > 1
            else "Unidade desvinculada com sucesso!"
        )

        return {
            "sucesso": True,
            "mensagem": mensagem,
        }
    
    @transaction.atomic
    def desvincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Desvincula as unidades do tipo de custeio.

        Parameters:
            unidades_uuid (List[str]): lista de UUIDs das unidades a serem desvinculadas

        Returns:
            Dict[str, Any]: status da operação
        """

        unidades = self._obter_unidades(unidades_uuid)

        if not unidades:
            raise ValidacaoVinculoException(
                "Nenhuma unidade foi identificada para desvínculo."
            )

        rateios = self.tipo_custeio.rateiodespesa_set
        qt_nao_removidas = 0

        for unidade in unidades:

            possui_rateios_completos = rateios.filter(
                Q(associacao__unidade=unidade) | 
                Q(despesa__associacao__unidade=unidade)              
            ).filter(despesa__status=STATUS_COMPLETO).exists()            

            if possui_rateios_completos:
                qt_nao_removidas += 1
                continue

            # Remove vínculo dos rateios em rascunho
            rateios.filter(
                associacao__unidade=unidade,
                despesa__status=STATUS_INCOMPLETO
            ).update(
                tipo_custeio=None,
                especificacao_material_servico=None
            )

            self.tipo_custeio.unidades.remove(unidade)

        if qt_nao_removidas == len(unidades):
            raise ValidacaoVinculoException(
                "Não é possível desvincular pois a(s) unidade(s) "
                "possuem lançamentos deste tipo."
            )

        mensagem = (
            "Unidades desvinculadas com sucesso!"
            if len(unidades) > 1
            else "Unidade desvinculada com sucesso!"
        )

        return {
            "sucesso": True,
            "mensagem": mensagem,
        }

    @transaction.atomic
    def desvincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Desvincula todas as unidades.
        """

        # Remove todos os vínculos
        self.tipo_custeio.unidades.clear()

        rateios_completos = self.tipo_custeio.rateiodespesa_set.filter(
            despesa__status=STATUS_COMPLETO
        )

        # Unidades que possuem rateios e não podem ser desvinculadas       
        unidades_com_despesas_completas = (
            rateios_completos
            .values_list('despesa__associacao__unidade', flat=True)
            .distinct()
        )
        
        # Recria vínculo com essas unidades
        self.tipo_custeio.unidades.add(*unidades_com_despesas_completas)

        # Remove vínculo dos rateios em rascunho
        self.tipo_custeio.rateiodespesa_set.filter(
            despesa__status=STATUS_INCOMPLETO,
        ).update(
            tipo_custeio=None,
            especificacao_material_servico=None
        )

        logger.warning("Todas as Unidades permitidas foram desvinculadas no Tipo Custeio.")

        return {
            "sucesso": True,
            "mensagem": "Todas as unidades permitidas foram desvinculadas com sucesso!",
        }
