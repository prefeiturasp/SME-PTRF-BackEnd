"""
Módulo de API para gerenciamento das receitas previstas.

Este módulo concentra os endpoints de  listar, consultar,
criar e atualizar registros.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

import django_filters
from waffle.mixins import WaffleFlagMixin

from ...models import ReceitaPrevistaPaa
from sme_ptrf_apps.paa.api.serializers import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.paa.mixins.paa_bloqueia_alteracao_mixin import PaaBloqueiaAlteracaoMixin
from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import TipoBloqueioPaa


class ReceitaPrevistaPaaFiltro(django_filters.FilterSet):
    """
    Define os filtros disponíveis para consulta da receita prevista.

    Permite filtrar receita prevista pelo outro_recurso_periodo_uuid, outro_recurso_uuid,
    periodo_paa_uuid, paa_uuid.
    """
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


class ReceitaPrevistaPaaViewSet(WaffleFlagMixin, PaaBloqueiaAlteracaoMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento das receitas previstas.

    Permite listar, consultar, criar e atualizar registros, com suporte à
    filtragem por meio do filtro configurado e paginação dos resultados.
    """
    waffle_flag = "paa"
    tipo_bloqueio_paa = TipoBloqueioPaa.STATUS_GERADO
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = ReceitaPrevistaPaa.objects.all()
    serializer_class = ReceitaPrevistaPaaSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = ReceitaPrevistaPaaFiltro
    http_method_names = ['get', 'post', 'patch']
