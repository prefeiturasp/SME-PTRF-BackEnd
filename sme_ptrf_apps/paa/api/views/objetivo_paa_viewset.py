"""
Módulo de API para gerenciamento dos objetivos do PAA.

Este módulo concentra os endpoints de listagem, consulta, criação, atualização e
remoção dos recursos próprios do PAA, permitindo a filtragem e paginação.
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

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import ObjetivoPaa
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices
from sme_ptrf_apps.paa.api.serializers import ObjetivoPaaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from drf_spectacular.utils import extend_schema_view
from sme_ptrf_apps.paa.api.views.docs.objetivo_paa_docs import DOCS

logger = logging.getLogger(__name__)


class ObjetivoPAAFilterBackend(django_filters.FilterSet):
    """
    FilterSet responsável pela filtragem dos objetivos do PAA.

    Permite filtrar os objetivos pelos seguintes campos:

    - nome
    - status
    - paa__uuid
    """
    nome = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    paa__uuid = django_filters.CharFilter(field_name="paa__uuid", lookup_expr="exact")

    class Meta:
        model = ObjetivoPaa
        fields = ['nome', 'status', 'paa__uuid']


@extend_schema_view(**DOCS)
class ObjetivoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento dos objetivos do PAA.

    Disponibiliza operações de listagem, consulta, criação, atualização e
    remoção dos recursos próprios do PAA, permitindo a filtragem e paginação.
    """
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = ObjetivoPaa.objects.filter(paa__isnull=True).order_by('nome')
    serializer_class = ObjetivoPaaSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ObjetivoPAAFilterBackend

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request: Request, *args, **kwrgs) -> Response:
        """
        Retorne as tabelas dos objetivos do PAA.
        """
        tabelas = dict(status=StatusChoices.to_dict())
        return Response(tabelas, status=status.HTTP_200_OK)
