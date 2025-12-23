from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import ReceitaPrevistaOutroRecursoPeriodo
from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaOutroRecursoPeriodoSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class ReceitaPrevistaOutroRecursoPeriodoFiltro(django_filters.FilterSet):
    outro_recurso_periodo_uuid = django_filters.CharFilter(
        field_name="outro_recurso_periodo__uuid", lookup_expr="exact", label="UUID Outro Recurso Período")
    outro_recurso_uuid = django_filters.CharFilter(
        field_name="outro_recurso_periodo__outro_recurso__uuid", lookup_expr="exact", label="UUID Outro Recurso")
    periodo_paa_uuid = django_filters.CharFilter(
        field_name="outro_recurso_periodo__periodo_paa__uuid", lookup_expr="exact", label="UUID Período PAA")

    class Meta:
        model = ReceitaPrevistaOutroRecursoPeriodo
        fields = ['outro_recurso_periodo_uuid', 'outro_recurso_uuid', 'periodo_paa_uuid']


class ReceitaPrevistaOutroRecursoPeriodoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ReceitaPrevistaOutroRecursoPeriodo.objects.all()
    serializer_class = ReceitaPrevistaOutroRecursoPeriodoSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ReceitaPrevistaOutroRecursoPeriodoFiltro
    http_method_names = ['get', 'post', 'patch']
