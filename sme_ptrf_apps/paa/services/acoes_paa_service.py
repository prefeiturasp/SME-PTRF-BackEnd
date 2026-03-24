import logging

from django.db.models import Q, QuerySet
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.core.models import Associacao

from waffle import get_waffle_flag_model

logger = logging.getLogger(__name__)


class AcoesPaaService:
    """
    Serviço para obtenção das Ações disponíveis para o PAA.

    Centraliza a lógica de filtragem para os três tipos de ação do PAA:
    - Ações PTRF              - obter_ptrf()                    Queryset
    - Ações PDDE              - obter_pdde()                    Queryset
    - Outros Recursos Período - obter_outros_recursos_periodo() Queryset
    """

    def __init__(self, paa: Paa):
        self.paa = paa
        self.associacao: Associacao = paa.associacao

    def _tem_flag_paa_retificacao(self):
        flags = get_waffle_flag_model()
        return flags.objects.filter(name='paa-retificacao', everyone=True).exists()

    def obter_ptrf(self) -> QuerySet:
        """
        Retorna o queryset de AcaoAssociacao filtrado para uso no PAA.

        Retorna ações onde a Ação PTRF:
        - Pertence a um Recurso legado (recurso__legado=True), E
        - Possui exibir_paa=True (ações correntes disponíveis para o PAA)
        Concatenado com as ações salvas em paa.acoes_conclusao, eliminando duplicatas.
        """
        qs_disponiveis = self.paa.associacao.acoes.filter(
            acao__recurso__legado=True, acao__exibir_paa=True
        )
        # FLAG(paa-retificacao):Condicional a ser removida quando a flag 'paa-retificacao' for removida definitivamente
        if not self._tem_flag_paa_retificacao():
            return qs_disponiveis

        # Ações Registradas no PAA
        acoes_conclusao = self.paa.acoes_conclusao.all()

        logger.info('Flag \'paa-retificacao\' encontrada. Carregando Ações PTRF + Ações salvas no PAA.')
        return self.associacao.acoes.filter(
            Q(acao__recurso__legado=True, acao__exibir_paa=True) |
            Q(acao__in=acoes_conclusao)
        ).distinct()

    def obter_pdde(self) -> QuerySet:
        """
        Retorna o queryset de AcaoPdde filtrado para uso no PAA.

        Retorna ações onde AcaoPdde:
        - Possui status=ATIVA (ações correntes disponíveis para o PAA), OU
        - Está salva em paa.acoes_pdde_conclusao (ações registradas no momento da conclusão do PAA)

        Garante que ações desativadas após a conclusão do PAA ainda sejam exibidas,
        pois estavam disponíveis no momento do registro.
        """
        from sme_ptrf_apps.paa.models import AcaoPdde

        qs_disponiveis = AcaoPdde.objects.filter(status=AcaoPdde.STATUS_ATIVA)

        # FLAG(paa-retificacao):Condicional a ser removida quando a flag 'paa-retificacao' for removida definitivamente
        if not self._tem_flag_paa_retificacao():
            return qs_disponiveis

        # Açoes registradas no PAA
        acoes_pdde_conclusao = self.paa.acoes_pdde_conclusao.all()

        logger.info('Flag \'paa-retificacao\' encontrada. Carregando Ações PDDE + Ações salvas no PAA.')
        return AcaoPdde.objects.filter(
            Q(pk__in=qs_disponiveis) |
            Q(pk__in=acoes_pdde_conclusao)
        ).distinct()

    def obter_outros_recursos_periodo(self) -> QuerySet:
        """
        Retorna o queryset de OutroRecursoPeriodoPaa filtrado para uso no PAA.

        Sempre reutiliza o manager disponiveis_para_paa (ativo=True, mesmo período,
        unidade da associação ou sem unidade vinculada).

        Quando a flag 'paa-retificacao' estiver ativa, concatena os recursos salvos
        em paa.outros_recursos_periodo_conclusao (registrados no momento da conclusão do PAA),
        garantindo que recursos desativados após a conclusão ainda sejam exibidos.
        """
        from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa

        qs_disponiveis = OutroRecursoPeriodoPaa.objects.disponiveis_para_paa(self.paa)
        # FLAG(paa-retificacao):Condicional a ser removida quando a flag 'paa-retificacao' for removida definitivamente
        if not self._tem_flag_paa_retificacao():
            return qs_disponiveis

        # Açoes registradas no PAA
        outros_recursos_conclusao = self.paa.outros_recursos_periodo_conclusao.all()

        return OutroRecursoPeriodoPaa.objects.filter(
            Q(pk__in=qs_disponiveis) | Q(pk__in=outros_recursos_conclusao)
        ).select_related('outro_recurso', 'periodo_paa').distinct()


class AcoesReceitasPrevistasPaaService(AcoesPaaService):
    """
        Esta Classe centraliza a lógica de obtenção das Receitas Previstas em
        cada Ação (PTRF, PDDE, Recursos Próprios)
    """
    def __init__(self, paa: Paa):
        super().__init__(paa)

    def serialized_ptrf_com_receitas_previstas(self):
        from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoRetrieveSerializer
        from sme_ptrf_apps.paa.api.serializers.receita_prevista_paa_serializer import ReceitaPrevistaPaaSerializer

        acoes = super().obter_ptrf()

        serialized_acoes = AcaoAssociacaoRetrieveSerializer(acoes, many=True).data

        for acao_assoc in serialized_acoes:
            acao_assoc['receitas_previstas_paa'] = ReceitaPrevistaPaaSerializer(
                self.paa.receitaprevistapaa_set.filter(
                    acao_associacao__acao__uuid=str(acao_assoc['acao']['uuid'])
                ),
                many=True).data
        return serialized_acoes

    def serialized_pdde_com_receitas_previstas(self, qs=None):
        from sme_ptrf_apps.paa.api.serializers.acao_pdde_serializer import (
            AcaoPddeSerializer)
        from sme_ptrf_apps.paa.models import ReceitaPrevistaPdde
        from sme_ptrf_apps.paa.api.serializers.receita_prevista_pdde_serializer import (
            ReceitasPrevistasPDDEValoresSerializer)

        # Condicional quando há necessidade de paginação na viewset, retornar apenas o queryset paginado
        acoes = super().obter_pdde() if not qs else qs

        serialized_acoes = AcaoPddeSerializer(acoes, many=True).data

        for serial_acao_pdde in serialized_acoes:
            qs_receitas_pdde = ReceitaPrevistaPdde.objects.filter(
                acao_pdde__uuid=serial_acao_pdde.get('uuid'),
                paa=self.paa
            ).first()

            serial_acao_pdde['receitas_previstas_pdde_valores'] = ReceitasPrevistasPDDEValoresSerializer(
                qs_receitas_pdde).data

        return serialized_acoes

    def serialized_outros_recursos_periodo_com_receitas_previstas(self):
        """
        Reutiliza o filtro de Outros recursos do Período do PAA, somente, ativos e
        Vinculados e referencia de receitas previstas.
        """
        from sme_ptrf_apps.paa.api.serializers.outros_recursos_periodo_paa_serializer import (
            OutrosRecursosPeriodoPaaSerializer)
        from sme_ptrf_apps.paa.models import ReceitaPrevistaOutroRecursoPeriodo
        from sme_ptrf_apps.paa.api.serializers.receita_prevista_outro_recurso_periodo_serializer import (
            ReceitaPrevistaOutroRecursoPeriodoSerializer)

        acoes = super().obter_outros_recursos_periodo()

        serialized_acoes = OutrosRecursosPeriodoPaaSerializer(acoes, many=True).data

        for serialized_outro_recurso in serialized_acoes:
            receita = ReceitaPrevistaOutroRecursoPeriodo.objects.filter(
                paa=self.paa,
                outro_recurso_periodo__uuid=serialized_outro_recurso['uuid'])
            serialized_outro_recurso['receitas_previstas'] = ReceitaPrevistaOutroRecursoPeriodoSerializer(
                receita, many=True).data

        return serialized_acoes
