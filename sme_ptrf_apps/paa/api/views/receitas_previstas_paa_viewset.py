from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import ReceitaPrevistaPaa
from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe


class ReceitaPrevistaPaaFiltro(django_filters.FilterSet):
    acao_uuid = django_filters.CharFilter(
        field_name="acao_associacao__acao__uuid", lookup_expr="exact", label="UUID da ação")
    associacao_uuid = django_filters.CharFilter(
        field_name="acao_associacao__associacao__uuid", lookup_expr="exact", label="UUID da Associação")
    acao_nome = django_filters.CharFilter(
        field_name="acao_associacao__acao__nome", lookup_expr="icontains", label="Nome da Ação")
    associacao_nome = django_filters.CharFilter(
        field_name="acao_associacao__associacao__nome", lookup_expr="icontains", label="Nome da Associação")
    unidade_eol = django_filters.CharFilter(
        field_name="acao_associacao__associacao__unidade__codigo_eol", lookup_expr="exact",
        label="Código EOL da Unidade")

    class Meta:
        model = ReceitaPrevistaPaa
        fields = [
            'acao_uuid',
            'associacao_uuid',
            'acao_nome',
            'associacao_nome',
            'unidade_eol',
        ]


class ReceitaPrevistaPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ReceitaPrevistaPaa.objects.all()
    serializer_class = ReceitaPrevistaPaaSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ReceitaPrevistaPaaFiltro
    http_method_names = ['get', 'post', 'patch']
