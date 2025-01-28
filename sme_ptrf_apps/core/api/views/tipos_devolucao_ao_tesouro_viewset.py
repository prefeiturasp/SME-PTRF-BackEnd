from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet

from ..serializers.tipo_devolucao_ao_tesouro_serializer import TipoDevolucaoAoTesouroSerializer
from ...models import TipoDevolucaoAoTesouro
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from ..utils.pagination import CustomPagination

class TiposDevolucaoAoTesouroViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     mixins.UpdateModelMixin,
                                     mixins.DestroyModelMixin,
                                     GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = TipoDevolucaoAoTesouro.objects.all()
    serializer_class = TipoDevolucaoAoTesouroSerializer

    def get_queryset(self):
        if self.action == 'list':
            filtrar_nome = self.request.query_params.get('nome')
            if filtrar_nome:
                return TipoDevolucaoAoTesouro.objects.filter(
                    nome__unaccent__icontains=filtrar_nome)

        return TipoDevolucaoAoTesouro.objects.all()

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há lançamentos ' +
                'cadastradas com esse motivo de devolução ao tesouro.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MotivosDevolucaoAoTesouroViewSet(mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin,
                                     mixins.CreateModelMixin,
                                     mixins.UpdateModelMixin,
                                     mixins.DestroyModelMixin,
                                     GenericViewSet):
    permission_classes = []#[IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = TipoDevolucaoAoTesouro.objects.all()
    serializer_class = TipoDevolucaoAoTesouroSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.action == 'list':
            filtrar_nome = self.request.query_params.get('nome')
            if filtrar_nome:
                return TipoDevolucaoAoTesouro.objects.filter(
                    nome__unaccent__icontains=filtrar_nome)

        return TipoDevolucaoAoTesouro.objects.all()

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há lançamentos ' +
                'cadastradas com esse motivo de devolução ao tesouro.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
