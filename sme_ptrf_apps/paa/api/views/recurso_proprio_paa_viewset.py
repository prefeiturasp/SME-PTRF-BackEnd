
"""
Módulo de API para gerenciamento dos recursos próprios do PAA.

Este módulo concentra os endpoints de listagem, consulta, criação, atualização e
remoção dos recursos próprios do PAA.
"""
import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from django.db import transaction
from django.db.models import Sum
import django_filters
from waffle.mixins import WaffleFlagMixin
from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import RecursoProprioPaa
from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import (
    RecursoProprioPaaCreateSerializer, RecursoProprioPaaListSerializer)
from .docs.recurso_proprio_paa_docs import DOCS

from sme_ptrf_apps.paa.mixins.paa_bloqueia_alteracao_mixin import PaaBloqueiaAlteracaoMixin
from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import TipoBloqueioPaa

logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
class RecursoProprioPaaViewSet(WaffleFlagMixin, PaaBloqueiaAlteracaoMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento dos recursos próprios do PAA.

    Disponibiliza operações de listagem, consulta, criação, atualização e
    remoção dos recursos próprios do PAA, permitindo a filtragem pelo associacao__uuid
    e paa__uuid.
    """
    waffle_flag = "paa"
    tipo_bloqueio_paa = TipoBloqueioPaa.STATUS_GERADO
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = RecursoProprioPaa.objects.all()
    serializer_class = RecursoProprioPaaListSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('associacao__uuid', 'paa__uuid')

    def get_serializer_class(self) -> type[Serializer]:
        """
        Retorne o serializer apropriado para a ação executada.

        Utiliza o serializer listagem para as operações de atualização e
        listagem, e o serializer create para as demais ações.

        Returns:
            Serializer: Classe do serializer correspondente à ação atual.
        """
        if self.action in ['retrieve', 'list']:
            return RecursoProprioPaaListSerializer
        else:
            return RecursoProprioPaaCreateSerializer

    def destroy(self, request, *args, **kwargs) -> Response:
        """Exclua um recursos próprios do PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Uma resposta indicando remoção bem-sucedida ou erro de proteção.
        """
        from django.db.models.deletion import ProtectedError
        from sme_ptrf_apps.paa.services import (
            PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService,
            ConfirmarExlusaoPrioridadesPaaRecursoProprioService
        )
        confirmar_limpeza_prioridades_paa = request.query_params.get('confirmar_limpeza_prioridades_paa')
        confirmar_limpeza_prioridades_paa = confirmar_limpeza_prioridades_paa in ['true', 'True', 1]

        obj = self.get_object()

        with transaction.atomic():
            recurso = {'valor': obj.valor}
            service = PrioridadesPaaImpactadasReceitasPrevistasRecursoProprioService(recurso, obj)
            try:
                service.limpar_valor_prioridades_impactadas_ao_excluir_instancia(confirmar_limpeza_prioridades_paa)
            except ConfirmarExlusaoPrioridadesPaaRecursoProprioService as e:
                return Response({"confirmar": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                msg_error = 'Falha ao limpar prioridades impactadas pelo Recurso Próprio!'
                logger.error(f'{msg_error}: {str(e)}')
                return Response(
                    {"mensagem": msg_error},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                self.perform_destroy(obj)
            except ProtectedError:
                content = {
                    'erro': 'ProtectedError',
                    'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a esse Recurso'
                }
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='total',
            permission_classes=[IsAuthenticated])
    def total_recursos(self, request, *args, **kwrgs) -> Response:
        """Retone o total dos recursos próprios do PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            O total dos recursos próprios do PAA.
        """
        queryset = self.filter_queryset(self.get_queryset())
        valor_total = queryset.aggregate(total=Sum('valor'))
        return Response({
            'total': valor_total['total']
        }, status=status.HTTP_200_OK)
