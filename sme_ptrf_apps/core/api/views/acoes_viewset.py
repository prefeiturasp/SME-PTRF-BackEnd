from django.db.models.query_utils import Q
from rest_framework import mixins, status
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from ..serializers.acao_serializer import AcaoSerializer
from ...models import Acao
from ...services import associacoes_nao_vinculadas_a_acao
from ..serializers.associacao_serializer import AssociacaoListSerializer


class AcoesViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Acao.objects.all().order_by('nome')
    serializer_class = AcaoSerializer

    def get_queryset(self):
        qs = Acao.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        return qs.order_by('nome')

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa ação não pode ser excluida porque está sendo usada.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='associacoes-nao-vinculadas')
    def associacoes_nao_vinculadas(self, request, uuid=None):
        acao = self.get_object()
        qs = associacoes_nao_vinculadas_a_acao(acao)

        result = AssociacaoListSerializer(qs, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='associacoes-nao-vinculadas-por-nome/(?P<nome>[^/.]+)')
    def associacoes_nao_vinculadas_por_nome(self, request, nome, uuid=None):
        acao = self.get_object()
        qs = associacoes_nao_vinculadas_a_acao(acao)

        if nome is not None:
            qs = qs.filter(Q(nome__unaccent__icontains=nome) | Q(
                unidade__nome__unaccent__icontains=nome) | Q(
                unidade__codigo_eol__icontains=nome))

        result = AssociacaoListSerializer(qs, many=True).data
        return Response(result, status=status.HTTP_200_OK)
