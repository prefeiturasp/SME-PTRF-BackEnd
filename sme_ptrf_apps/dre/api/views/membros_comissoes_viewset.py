from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from ...models import MembroComissao
from ..serializers.membro_comissao_serializer import (
    MembroComissaoListSerializer,
    MembroComissaoCreateSerializer,
    MembroComissaoRetrieveSerializer
)

from sme_ptrf_apps.dre.services import MembroComissaoService

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
)

from drf_spectacular.utils import extend_schema_view
from .docs.membros_comissoes_docs import DOCS


@extend_schema_view(**DOCS)
class MembrosComissoesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = MembroComissao.objects.all().order_by('nome')
    serializer_class = MembroComissaoListSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filterset_fields = ('dre__uuid',)

    def get_queryset(self):
        qs = MembroComissao.objects.all().order_by('nome')

        nome_ou_rf = self.request.query_params.get('nome_ou_rf')
        if nome_ou_rf is not None:
            qs = qs.filter(Q(nome__unaccent__icontains=nome_ou_rf) | Q(
                rf=nome_ou_rf))

        comissao_uuid = self.request.query_params.get('comissao_uuid')
        if comissao_uuid is not None:
            qs = qs.filter(comissoes__uuid=comissao_uuid)

        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return MembroComissaoCreateSerializer
        elif self.action == 'retrieve':
            return MembroComissaoRetrieveSerializer
        else:
            return MembroComissaoListSerializer

    def destroy(self, request, *args, **kwargs):
        """
        Remove um membro da comissão e das atas em elaboração em que ele está presente.

        Obtém o membro a partir da requisição, realiza sua exclusão por meio
        do serviço MembroComissaoService e retorna HTTP 204 (No Content)
        em caso de sucesso.
        """
        instance = self.get_object()

        MembroComissaoService.deletar_membro(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)
