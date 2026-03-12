import logging
from django.db import transaction
from typing import List, Dict, Any
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.receitas.models import TipoReceita

logger = logging.getLogger(__name__)


class ValidacaoVinculoException(Exception):
    """Exceção lançada quando uma validação de vínculo falha."""
    pass


class UnidadeNaoEncontradaException(Exception):
    """Exceção lançada quando uma unidade não é encontrada."""
    pass


class TipoReceitaVinculoUnidadeService:

    """
    Este service centraliza todas as operações de vínculo, desvínculo de unidades e validações.
    """

    def __init__(self, tipo_receita: TipoReceita):
        self.tipo_receita = tipo_receita

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
    def vincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Vincula as unidades do tipo receita.

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

               
        self.tipo_receita.unidades.add(*unidades)

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
    def vincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Vincula todas as unidades.

        Não valida se o tipo receita precisa de confirmação para vinculo
        Apenas habilita para todas as unidades

        Returns:
            Dicionário com status da operação

        """

        unidades = list(self.tipo_receita.unidades.all())

        if not unidades:
            return {
                'sucesso': True,
                'mensagem': 'Todas as Unidades já estão habilitadas no Tipo Receita.',
            }

        # Remove todas as unidades
        self.tipo_receita.unidades.clear()

        logger.warning("Todas as Unidades foram habilitadas no Tipo Receita.")

        return {
            'sucesso': True,
            'mensagem': 'Todas as unidades foram habilitadas com sucesso!',
        }

    @transaction.atomic
    def desvincular_unidades(self, unidades_uuid: List[str]) -> Dict[str, Any]:
        """
        Desvincula as unidades do tipo receita.

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
            possui_receitas = self.tipo_receita.receita_set.filter(
                associacao__unidade=unidade
            ).exists()

            if possui_receitas:
                qt_nao_removidas += 1
                continue

            self.tipo_receita.unidades.remove(unidade)

        if qt_nao_removidas == len(unidades):
            raise ValidacaoVinculoException(
                "Não é possível desvincular a(s) unidade(s) "
                "pois as unidades possuem crédito vinculado."
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

    @transaction.atomic
    def desvincular_todas_unidades(self) -> Dict[str, Any]:
        """
        Desvincula todas as unidades.
        """

        # Remove todos os vínculos
        self.tipo_receita.unidades.clear()

        # Unidades que possuem receitas e não podem ser desvinculadas
        unidades_com_receita = (
            self.tipo_receita.receita_set
            .values_list('associacao__unidade', flat=True)
            .distinct()
        )

        # Recria vínculo com essas unidades
        self.tipo_receita.unidades.add(*unidades_com_receita)

        logger.warning("Todas as Unidades permitidas foram desvinculadas no Tipo Receita.")

        return {
            "sucesso": True,
            "mensagem": "Todas as unidades permitidas foram desvinculadas com sucesso!",
        }