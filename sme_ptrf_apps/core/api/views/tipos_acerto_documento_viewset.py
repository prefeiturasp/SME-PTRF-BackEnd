from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ..serializers.tipo_acerto_documento_serializer import (
    TipoAcertoDocumentoSerializer,
    TipoAcertoDocumentoListaSerializer
)
from ...models import TipoAcertoDocumento, TipoDocumentoPrestacaoConta
from sme_ptrf_apps.users.permissoes import PermissaoApiDre
from rest_framework.response import Response
from rest_framework.decorators import action
from ....utils.choices_to_json import choices_to_json


class TiposAcertoDocumentoViewSet(mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.CreateModelMixin,
                                  mixins.UpdateModelMixin,
                                  mixins.DestroyModelMixin,
                                  GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = TipoAcertoDocumento.objects.all()
    serializer_class = TipoAcertoDocumentoListaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('tipos_documento_prestacao__uuid',)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return TipoAcertoDocumentoListaSerializer
        else:
            return TipoAcertoDocumentoSerializer

    def get_queryset(self):
        qs = TipoAcertoDocumento.objects.all()

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

        documento_relacionado = self.request.query_params.get('documento_relacionado')
        documento_list = documento_relacionado.split(',') if documento_relacionado else []
        if documento_list:
            qs = qs.filter(tipos_documento_prestacao__id__in=documento_list)

        return qs.order_by('id')

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Esse tipo de documento não pode ser excluído pois existem solicitações de acertos com ele'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoApiDre])
    def tabelas(self, request):
        tipos_documento_prestacao__uuid = self.request.query_params.get('tipos_documento_prestacao__uuid', None)

        result = {
            "categorias": TipoAcertoDocumento.categorias(),
            "agrupado_por_categorias": TipoAcertoDocumento.agrupado_por_categoria(tipos_documento_prestacao__uuid),
            "documentos": TipoDocumentoPrestacaoConta.lista_documentos(),
        }

        return Response(result, status=status.HTTP_200_OK)

