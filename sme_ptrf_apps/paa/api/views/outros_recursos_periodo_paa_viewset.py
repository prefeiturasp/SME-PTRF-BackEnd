from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import django_filters
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.paa.api.serializers import OutrosRecursosPeriodoPaaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoApiSME


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

    @action(
        detail=True,
        methods=['post'],
        url_path='importar-unidades',
        permission_classes=[IsAuthenticated & PermissaoApiSME]
    )
    def importar_unidades(self, request, uuid=None):
        destino = self.get_object()
        origem_uuid = request.data.get('origem_uuid')

        if not origem_uuid:
            return Response(
                {'detail': 'origem_uuid é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            origem = OutroRecursoPeriodoPaa.objects.get(uuid=origem_uuid)
        except OutroRecursoPeriodoPaa.DoesNotExist:
            return Response(
                {'detail': 'Recurso de origem não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        for unidade in origem.unidades.all():
            destino.unidades.add(unidade)

        return Response(
            {'detail': 'Unidades importadas com sucesso.'},
            status=status.HTTP_200_OK
        )
