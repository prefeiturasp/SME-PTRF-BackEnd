from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import ReceitaPrevistaPdde
from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaPddeSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class ReceitaPrevistaPddeFiltro(django_filters.FilterSet):
    acao_uuid = django_filters.CharFilter(
        field_name="acao_pdde__uuid", lookup_expr="exact", label="UUID da Ação PDDE")
    acao_nome = django_filters.CharFilter(
        field_name="acao_pdde__nome", lookup_expr="icontains", label="Nome da Ação PDDE")
    paa_uuid = django_filters.CharFilter(
        field_name="paa__uuid", lookup_expr="exact", label="UUID do PAA")
    programa_uuid = django_filters.CharFilter(
        field_name="acao_pdde__programa__uuid", lookup_expr="exact", label="UUID do Programa")
    programa_nome = django_filters.CharFilter(
        field_name="acao_pdde__programa__nome", lookup_expr="icontains", label="Nome do Programa")

    class Meta:
        model = ReceitaPrevistaPdde
        fields = [
            'acao_uuid',
            'acao_nome',
            'paa_uuid',
            'programa_uuid',
            'programa_nome',
        ]


class ReceitaPrevistaPddeViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ReceitaPrevistaPdde.objects.all()
    serializer_class = ReceitaPrevistaPddeSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ReceitaPrevistaPddeFiltro
    http_method_names = ['post', 'patch']
