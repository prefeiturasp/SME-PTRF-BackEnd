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
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

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
    queryset = AtividadeEstatutaria.objects.filter(paa__isnull=True).order_by('mes', 'nome')
    serializer_class = AtividadeEstatutariaSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AtividadeEstatutariaPaaFilterBackend

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(
            status=StatusChoices.to_dict(),
            mes=Mes.to_dict(),
            tipo=TipoAtividadeEstatutariaEnum.to_dict(),
        )
        return Response(tabelas, status=status.HTTP_200_OK)
