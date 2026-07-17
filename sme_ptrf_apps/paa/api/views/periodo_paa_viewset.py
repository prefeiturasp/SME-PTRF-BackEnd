"""
Módulo de API para gerenciamento dos períodos do Plano Anual de Atividades (PAA).

Este módulo concentra os endpoints para listagem, consulta, criação, atualização e
remoção de períodos PAA.
"""
import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from django.http import Http404
from django.db.models import Count, Q, QuerySet
from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPIApenasSmeComLeituraOuGravacao
)
from sme_ptrf_apps.paa.api.serializers.periodo_paa_serializer import PeriodoPaaSerializer
from sme_ptrf_apps.paa.models import PeriodoPaa, Paa
from .docs.periodo_paa_docs import DOCS

logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
class PeriodoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento dos períodos PAA.

    Disponibiliza operações de listagem, consulta, criação, atualização e
    remoção de períodos PAA, além de permitir a filtragem por referência e
    por outro recurso ativo vinculado ao período.
    """
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoAPIApenasSmeComLeituraOuGravacao]
    lookup_field = 'uuid'
    queryset = PeriodoPaa.objects.all()
    serializer_class = PeriodoPaaSerializer
    pagination_class = CustomPagination

    def get_queryset(self) -> QuerySet:
        """
        Retorne a queryset de períodos PAA.

        A consulta ordena os períodos por data inicial e referência, adiciona
        a quantidade de outros recursos ativos vinculados a cada período e
        permite filtrar pelos parâmetros de consulta `referencia` e
        `outro_recurso`.

        Returns:
            QuerySet: Queryset de períodos PAA filtrada e anotada.
        """
        qs = self.queryset.order_by('-data_inicial', 'referencia')

        # Adiciona a contagem de recursos habilitados no período
        qs = qs.annotate(
            qtd_outros_recursos_habilitados=Count(
                'outrorecursoperiodopaa',
                filter=Q(outrorecursoperiodopaa__ativo=True)
            )
        )

        filtro_referencia = self.request.query_params.get('referencia', None)
        if filtro_referencia:
            qs = qs.filter(referencia__unaccent__icontains=filtro_referencia)

        # filtrar Períodos que tenham vinculado o outro recurso(somente ativos) informado no filtro
        filtro_outro_recurso_uuid = self.request.query_params.get('outro_recurso', None)
        if filtro_outro_recurso_uuid:
            qs = qs.filter(
                outrorecursoperiodopaa__outro_recurso__uuid=filtro_outro_recurso_uuid,
                outrorecursoperiodopaa__ativo=True
            ).distinct()

        return qs

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Exclua um período PAA que não esteja vincula a algum PAA.

        Args:
            UUID: uuid do período PAA.

        Returns:
            204	Período removido com sucesso.
        """
        try:
            # Obtém o período que será excluído
            periodo = self.get_object()
            tem_paa_vinculado = Paa.objects.filter(periodo_paa=periodo).exists()

            # Verifica se o período está vinculado a algum PAA
            if tem_paa_vinculado:
                return Response(
                    {
                        "mensagem": (
                            "Este período de PAA não pode ser excluído porque está sendo utilizada em "
                            "um Plano Anual de Atividades (PAA).")
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verifica se tem 'Outro Recurso' vinculado ao período
            tem_outro_recurso_vinculado = periodo.outrorecursoperiodopaa_set.exists()
            if tem_outro_recurso_vinculado:
                return Response(
                    {
                        "mensagem": (
                            "Este período de PAA não pode ser excluído porque há "
                            "vínculos de 'Outro Recurso' associado.")
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            return super().destroy(request, *args, **kwargs)

        except Http404:
            return Response(
                {"mensagem": "Período não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"mensagem": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
