from rest_framework import mixins, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from ..serializers.tipo_acerto_lancamento_serializer import TipoAcertoLancamentoSerializer
from ...models import TipoAcertoLancamento
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
            "Retorna a lista de tipos de acerto de lançamento. "
            "Permite filtrar por **nome**, **categoria** (pode ser múltipla, separada por vírgula) "
            "e **ativo**."
        ),
        parameters=[
            OpenApiParameter("nome", str, OpenApiParameter.QUERY,
                             description="Filtra pelo nome (case-insensitive, acento ignorado)"),
            OpenApiParameter("categoria", str, OpenApiParameter.QUERY,
                             description="Filtra por categorias (separadas por vírgula)"),
            OpenApiParameter("ativo", bool, OpenApiParameter.QUERY, description="Filtra por ativo (true/false)"),
        ],
        responses={200: TipoAcertoLancamentoSerializer(many=True)},
    ),
    tabelas=extend_schema(
        description=(
            "Retorna as categorias disponíveis e os tipos de acerto agrupados por categoria. "
            "Aceita filtros opcionais."
        ),
        parameters=[
            OpenApiParameter("aplicavel_despesas_periodos_anteriores", bool, OpenApiParameter.QUERY,
                             description="Se filtra por aplicável a despesas de períodos anteriores"),
            OpenApiParameter("is_repasse", bool, OpenApiParameter.QUERY, description="Se filtra por ser repasse"),
        ],
        responses={
            200: inline_serializer(
                name="TabelaTiposAcertoLancamento",
                fields={
                    "categorias": serializers.ListField(child=serializers.CharField()),
                    "agrupado_por_categorias": serializers.DictField(),
                },
            ),
        },
    )
)
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
        aplicavel_despesas_periodos_anteriores = request.query_params.get('aplicavel_despesas_periodos_anteriores')
        is_repasse = request.query_params.get('is_repasse')

        result = {
            "categorias": TipoAcertoLancamento.categorias(),
            "agrupado_por_categorias": TipoAcertoLancamento.agrupado_por_categoria(
                aplicavel_despesas_periodos_anteriores, is_repasse)
        }

        return Response(result, status=status.HTTP_200_OK)
