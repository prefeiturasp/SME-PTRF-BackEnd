from django_filters import rest_framework as filters
from rest_framework import mixins, status, serializers
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
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    inline_serializer
)


@extend_schema_view(
    list=extend_schema(
        description=(
            "Retorna a lista de tipos de acerto de documento. "
            "Permite filtrar por **nome**, **categoria**, **ativo**, "
            "**documento_relacionado** e também pelo campo relacional "
            "**tipos_documento_prestacao__uuid**."
        ),
        parameters=[
            OpenApiParameter("nome", str, OpenApiParameter.QUERY,
                             description="Filtra pelo nome (case-insensitive, acento ignorado)"),
            OpenApiParameter("categoria", str, OpenApiParameter.QUERY,
                             description="Filtra por categorias (separadas por vírgula)"),
            OpenApiParameter("ativo", bool, OpenApiParameter.QUERY, description="Filtra por ativo (true/false)"),
            OpenApiParameter("documento_relacionado", str, OpenApiParameter.QUERY,
                             description="Filtra pelos IDs de documentos relacionados (separados por vírgula)"),
        ],
        responses={200: TipoAcertoDocumentoListaSerializer(many=True)},
    ),
    tabelas=extend_schema(
        description=(
            "Retorna as categorias disponíveis, os tipos de acerto agrupados por categoria "
            "e a lista de documentos de prestação de contas."
        ),
        parameters=[
            OpenApiParameter("tipos_documento_prestacao__uuid", str, OpenApiParameter.QUERY,
                             description="Filtra pelo UUID de TipoDocumentoPrestacaoConta"),
        ],
        responses={
            200: inline_serializer(
                name="TabelaTiposAcertoDocumento",
                fields={
                    "categorias": serializers.ListField(child=serializers.CharField()),
                    "agrupado_por_categorias": serializers.DictField(),
                    "documentos": serializers.ListField(child=serializers.DictField()),
                },
            ),
        },
    )
)
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
    filterset_fields = ('tipos_documento_prestacao__uuid',)

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
