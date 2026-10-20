"""
Módulo de API para gerenciamento dos recursos das atividades estatutárias.

Este módulo concentra os endpoints de criar, atualizar, ordenar e excluir atividades
estatutárias.
"""
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
import django_filters
from waffle.mixins import WaffleFlagMixin
from django.db.models import QuerySet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum, TipoAnosAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes, StatusChoices
from sme_ptrf_apps.paa.api.serializers import AtividadeEstatutariaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoApiSME
from drf_spectacular.utils import extend_schema_view
from sme_ptrf_apps.paa.api.views.docs.atividade_estatutaria_docs import DOCS
from sme_ptrf_apps.paa.services.atividade_estatutaria_service import AtividadeEstatutariaOrdenacaoService

logger = logging.getLogger(__name__)


class AtividadeEstatutariaPaaFilterBackend(django_filters.FilterSet):
    """
    FilterSet responsável pela filtragem das atividades estatutarias.

    Permite filtrar as ações pelos seguintes campos:

    - nome;
    - tipo;
    - ano
    - mes;
    - status;
    """
    nome = django_filters.CharFilter(field_name="nome", lookup_expr='icontains')
    tipo = django_filters.CharFilter(field_name="tipo", lookup_expr='exact')
    ano = django_filters.CharFilter(field_name="ano", lookup_expr="exact")
    mes = django_filters.CharFilter(field_name="mes", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = AtividadeEstatutaria
        fields = ['nome', 'tipo', 'status', 'ano', 'mes']


@extend_schema_view(**DOCS)
class AtividadeEstatutariaViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento das atividades estatutárias.

    Disponibiliza operações de criar, atualizar, ordenar e excluir atividades
    estatutárias.
    """
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    serializer_class = AtividadeEstatutariaSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AtividadeEstatutariaPaaFilterBackend

    def get_queryset(self) -> QuerySet[AtividadeEstatutaria]:
        """
        Retorne o queryset de atividades estatutarias ordenado.
        """
        return AtividadeEstatutariaOrdenacaoService.obter_queryset_ordenado()

    def perform_create(self, serializer) -> None:
        """
        Crie uma nova atividade estatutária utilizando o serviço de ordenação.

        Args:
            serializer: Serializer contendo os dados validados da nova atividade estatutária.

        """
        instance = AtividadeEstatutariaOrdenacaoService.create_atividade_estatutaria(
            validated_data=serializer.validated_data,
        )
        serializer.instance = instance

    def perform_destroy(self, instance) -> None:
        """
        Remove uma atividade estatutária utilizando o serviço de ordenação.

        Args:
            instance: Instância da atividade estatutária a ser removida.
        """
        AtividadeEstatutariaOrdenacaoService.delete_atividade_estatutaria(atividade=instance)

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request: Request, *args, **kwrgs) -> Response:
        """
        Retorne as tabelas de referência para atividades estatutárias.
        """
        tabelas = dict(
            status=StatusChoices.to_dict(),
            ano=TipoAnosAtividadeEstatutariaEnum.to_dict(),
            mes=Mes.to_dict(),
            tipo=TipoAtividadeEstatutariaEnum.to_dict(),
        )
        return Response(tabelas, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='ordenar', permission_classes=[PermissaoApiSME])
    def ordenar(self, request: Request, uuid: str | None = None) -> Response:
        """
        Atualize a ordenação das atividades estatutárias.

        Args:
            uuid: UUID da atividade estatutária a ser movida.
            uuid_destino: UUID da atividade estatutária de destino.
        """
        uuid_destino = request.data.get("destino")

        if not uuid_destino:
            return Response(
                {"mensagem": "UUID de destino não informado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            AtividadeEstatutariaOrdenacaoService.mover(
                uuid_origem=uuid,
                uuid_destino=uuid_destino,
            )
            return Response(
                {"mensagem": "Ordenação atualizada com sucesso."},
                status=status.HTTP_200_OK
            )

        except AtividadeEstatutaria.DoesNotExist:
            return Response(
                {"mensagem": "Atividade não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {
                    "mensagem": "Erro ao atualizar ordenação.",
                    "erro": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
