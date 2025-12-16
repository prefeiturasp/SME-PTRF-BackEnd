from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
import django_filters
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.paa.api.serializers import OutrosRecursosPeriodoPaaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class OutroRecursoPeriodoPaaFiltro(django_filters.FilterSet):
    periodo_paa_uuid = django_filters.CharFilter(lookup_expr='exact', field_name='periodo_paa__uuid')
    outro_recurso_uuid = django_filters.CharFilter(lookup_expr='exact', field_name='outro_recurso__uuid')
    outro_recurso_nome = django_filters.CharFilter(lookup_expr='icontains', field_name='outro_recurso__nome')
    ativo = django_filters.BooleanFilter(lookup_expr='exact')

    class Meta:
        model = OutroRecursoPeriodoPaa
        fields = ['periodo_paa_uuid', 'outro_recurso_uuid']


class OutrosRecursosPeriodoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OutroRecursoPeriodoPaa.objects.select_related('periodo_paa', 'outro_recurso').all()
    serializer_class = OutrosRecursosPeriodoPaaSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = OutroRecursoPeriodoPaaFiltro
