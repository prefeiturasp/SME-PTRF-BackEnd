import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import AtividadeEstatutaria
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes, StatusChoices
from sme_ptrf_apps.paa.api.serializers import AtividadeEstatutariaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoApiSME
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from sme_ptrf_apps.paa.services.atividade_estatutaria_service import AtividadeEstatutariaOrdenacaoService

logger = logging.getLogger(__name__)


class AtividadeEstatutariaPaaFilterBackend(django_filters.FilterSet):
    nome = django_filters.CharFilter(field_name="nome", lookup_expr='icontains')
    tipo = django_filters.CharFilter(field_name="tipo", lookup_expr='exact')
    mes = django_filters.CharFilter(field_name="mes", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = AtividadeEstatutaria
        fields = ['nome', 'tipo', 'status', 'mes']


@extend_schema_view(
    list=extend_schema(
        description=(
            "Retorna a lista de Atividades Estatutárias. "
            "Permite filtrar por **nome**, **status**, **tipo** e **mes**"
        ),
        parameters=[
            OpenApiParameter("nome", str, OpenApiParameter.QUERY,
                             description="Filtra pelo nome (case-insensitive, acento ignorado)"),
            OpenApiParameter("tipo", str, OpenApiParameter.QUERY,
                             description="Filtra pelo tipo de atividade",
                             enum=list(TipoAtividadeEstatutariaEnum.choices())),
            OpenApiParameter("mes", str, OpenApiParameter.QUERY,
                             description="Filtra por Mês", enum=list(Mes.choices)),
            OpenApiParameter("status", str, OpenApiParameter.QUERY,
                             description="Filtra por Status (0 / 1)", enum=list(StatusChoices.choices)),
        ],
        responses={200: AtividadeEstatutariaSerializer(many=True)},
    )
)
class AtividadeEstatutariaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    serializer_class = AtividadeEstatutariaSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AtividadeEstatutariaPaaFilterBackend

    def get_queryset(self):
        return AtividadeEstatutariaOrdenacaoService.obter_queryset_ordenado()

    def perform_create(self, serializer):
        instance = AtividadeEstatutariaOrdenacaoService.create_atividade_estatutaria(
            validated_data=serializer.validated_data,
        )
        serializer.instance = instance

    def perform_destroy(self, instance):
        AtividadeEstatutariaOrdenacaoService.delete_atividade_estatutaria(atividade=instance)

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(
            status=StatusChoices.to_dict(),
            mes=Mes.to_dict(),
            tipo=TipoAtividadeEstatutariaEnum.to_dict(),
        )
        return Response(tabelas, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='ordenar', permission_classes=[PermissaoApiSME])
    def ordenar(self, request, uuid=None):
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
