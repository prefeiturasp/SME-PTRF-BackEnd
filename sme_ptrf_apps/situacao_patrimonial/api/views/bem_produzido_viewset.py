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
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoSerializer, BemProduzidoSaveSerializer, BemProduzidoSaveRacunhoSerializer

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
            return BemProduzidoSaveSerializer
        return BemProduzidoSerializer

    @action(detail=True, methods=['post'], url_path='excluir-lote', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def excluir_em_lote(self, request, *args, **kwargs):
        bem_produzido = self.get_object()
        uuids_despesas = request.data.get('uuids', [])

        if not isinstance(uuids_despesas, list) or not all(isinstance(u, str) for u in uuids_despesas):
            return Response({'mensagem': 'A lista de UUIDs das despesas é obrigatória e deve conter apenas strings.'}, status=status.HTTP_400_BAD_REQUEST)

        despesas_remover = BemProduzidoDespesa.objects.filter(
            despesa__uuid__in=uuids_despesas,
            bem_produzido=bem_produzido
        )

        quantidade = despesas_remover.count()
        despesas_remover.delete()

        if bem_produzido.status == 'COMPLETO':
            bem_produzido.status = 'RASCUNHO'
            bem_produzido.save()

        return Response({
            'mensagem': f'{quantidade} despesas removidas do bem produzido.'
        }, status=status.HTTP_200_OK)


class BemProduzidoRascunhoViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = BemProduzido.objects.all()
    serializer_class = BemProduzidoSaveRacunhoSerializer
    http_method_names = ['post', 'patch']
    lookup_field = 'uuid'
