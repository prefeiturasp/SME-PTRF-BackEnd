import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido, BemProduzidoDespesa
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoSerializer, BemProduzidoCreateSerializer

logger = logging.getLogger(__name__)


class BemProduzidoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = BemProduzido.objects.all().order_by('id')
    serializer_class = BemProduzidoSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BemProduzidoCreateSerializer
        return BemProduzidoSerializer

    @action(detail=True, methods=['post'], url_path='excluir-lote', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def excluir_em_lote(self, request, *args, **kwargs):
        bem_produzido = self.get_object()
        uuids_para_remover = request.data.get('uuids', [])

        if not isinstance(uuids_para_remover, list) or not all(isinstance(u, str) for u in uuids_para_remover):        
            return Response({'mensagem': 'A lista de UUIDs é obrigatória e deve conter apenas strings.'}, status=status.HTTP_400_BAD_REQUEST)

        despesas_remover = BemProduzidoDespesa.objects.filter(
            uuid__in=uuids_para_remover,
            bem_produzido=bem_produzido
        )

        quantidade = despesas_remover.count()
        despesas_remover.delete()

        return Response({
            'mensagem': f'{quantidade} despesas removidas do bem produzido.'
        }, status=status.HTTP_200_OK)