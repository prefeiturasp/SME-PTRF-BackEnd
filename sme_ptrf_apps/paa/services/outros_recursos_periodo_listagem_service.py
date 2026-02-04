
from sme_ptrf_apps.core.models.unidade import Unidade
from sme_ptrf_apps.paa.models import (
    OutroRecursoPeriodoPaa, Paa, ReceitaPrevistaOutroRecursoPeriodo
)
from sme_ptrf_apps.paa.api.serializers.receita_prevista_outro_recurso_periodo_serializer import (
    ReceitaPrevistaOutroRecursoPeriodoSerializer)
from sme_ptrf_apps.paa.api.serializers.outros_recursos_periodo_paa_serializer import (
    OutrosRecursosPeriodoPaaSerializer)
import logging

logger = logging.getLogger(__name__)


class OutroRecursoPeriodoPaaListagemService:
    def __init__(self, paa: Paa, unidade: Unidade):
        self.paa = paa
        self.unidade = unidade

    def queryset_listar_outros_recursos_periodo_unidade(self):
        """
        Retorna uma lista de recursos vinculados ao Período do PAA,
        filtrados por período, ativo e vinculados a uma unidade.
        A lista é ordenada por nome do recurso.
        """
        return OutroRecursoPeriodoPaa.objects.disponiveis_para_paa(self.paa).order_by('outro_recurso__nome')

    def serialized_listar_outros_recursos_periodo_unidades(self):
        """
        Retorna uma lista de recursos vinculados ao Período do PAA,
        filtrados por período, ativo, serializados.
        """
        return OutrosRecursosPeriodoPaaSerializer(
            self.queryset_listar_outros_recursos_periodo_unidade(), many=True).data

    def serialized_listar_outros_recursos_periodo_receitas_previstas(self, paa):
        """
        Reutiliza o filtro de Outros recursos do Período do PAA, somente, ativos e
        Vinculados e referencia de receitas previstas
        """
        serialized_outros_recursos_periodo = self.serialized_listar_outros_recursos_periodo_unidades()

        for serialized_outro_recurso in serialized_outros_recursos_periodo:
            receita = ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
                paa=paa,
                outro_recurso_periodo__uuid=serialized_outro_recurso['uuid'])
            serialized_outro_recurso['receitas_previstas'] = ReceitaPrevistaOutroRecursoPeriodoSerializer(
                receita, many=True).data

        return serialized_outros_recursos_periodo
