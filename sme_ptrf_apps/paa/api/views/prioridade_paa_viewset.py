from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

import django_filters
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import PrioridadePaa
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.paa.api.serializers import (
    PrioridadePaaCreateSerializer,
    PrioridadePaaListSerializer
)
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa


class PrioridadePaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrioridadePaa.objects.all()
    serializer_class = PrioridadePaaCreateSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = (
        'acao_associacao__uuid',
        'paa__uuid',
        'recurso',
        'prioridade',  # 0 (False) ou 1 (True)
        'programa_pdde__uuid',
        'acao_pdde__uuid',
        'tipo_aplicacao',
        'tipo_despesa_custeio__uuid',
        'especificacao_material__uuid',
    )

    def get_queryset(self):
        qs = super().get_queryset()
        qs = queryset_prioridades_paa(qs)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return PrioridadePaaListSerializer
        else:
            return PrioridadePaaCreateSerializer

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request, *args, **kwrgs):
        tabelas = dict(
            prioridades=SimNaoChoices.to_dict(),
            recursos=RecursoOpcoesEnum.to_dict(),
            tipos_aplicacao=TipoAplicacaoOpcoesEnum.to_dict(),
        )

        return Response(tabelas, status=status.HTTP_200_OK)
