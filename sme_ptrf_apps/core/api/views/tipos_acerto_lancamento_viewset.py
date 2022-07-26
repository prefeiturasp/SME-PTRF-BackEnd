from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ..serializers.tipo_acerto_lancamento_serializer import TipoAcertoLancamentoSerializer
from ...models import TipoAcertoLancamento
from sme_ptrf_apps.users.permissoes import PermissaoApiDre
from rest_framework.response import Response
from rest_framework.decorators import action
from ....utils.choices_to_json import choices_to_json


class TiposAcertoLancamentoViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.CreateModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = TipoAcertoLancamento.objects.all()
    serializer_class = TipoAcertoLancamentoSerializer

    def get_queryset(self):
        qs = TipoAcertoLancamento.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(nome__unaccent__icontains=nome)

        categoria = self.request.query_params.get('categoria')
        categoria_list = categoria.split(',') if categoria else []
        if categoria_list:
            qs = qs.filter(categoria__in=categoria_list)

        ativo = self.request.query_params.get('ativo')
        if ativo is not None:
            qs = qs.filter(ativo=ativo)

        return qs.order_by('id')

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Esse tipo de lançamento não pode ser excluído pois existem solicitações de acertos com ele'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def tabelas(self, request):
        result = {
            "categorias": choices_to_json(TipoAcertoLancamento.CATEGORIA_CHOICES)
        }

        return Response(result, status=status.HTTP_200_OK)
