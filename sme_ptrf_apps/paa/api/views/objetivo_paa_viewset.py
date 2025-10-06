import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import ObjetivoPaa
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices
from sme_ptrf_apps.paa.api.serializers import ObjetivoPaaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

logger = logging.getLogger(__name__)


class ObjetivoPAAFilterBackend(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    paa__uuid = django_filters.CharFilter(field_name="paa__uuid", lookup_expr="exact")

    class Meta:
        model = ObjetivoPaa
        fields = ['nome', 'status', 'paa__uuid']


@extend_schema_view(
    list=extend_schema(
        description=(
            "Retorna a lista de objetivos do PAA. "
            "Permite filtrar por **nome**, **status**, "
            "e também pelo campo relacional **paa__uuid**."
        ),
        parameters=[
            OpenApiParameter("nome", str, OpenApiParameter.QUERY,
                             description="Filtra pelo nome (case-insensitive, acento ignorado)"),
            OpenApiParameter("status", str, OpenApiParameter.QUERY,
                             description="Filtra por Status (0 / 1)", enum=list(StatusChoices.choices)),
            OpenApiParameter("paa__uuid", bool, OpenApiParameter.QUERY,
                             description="Filtra pelo UUID do PAA"),
        ],
        responses={200: ObjetivoPaaSerializer(many=True)},
    )
)
class ObjetivoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = ObjetivoPaa.objects.all().order_by('nome')
    serializer_class = ObjetivoPaaSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ObjetivoPAAFilterBackend

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(status=StatusChoices.to_dict())
        return Response(tabelas, status=status.HTTP_200_OK)
