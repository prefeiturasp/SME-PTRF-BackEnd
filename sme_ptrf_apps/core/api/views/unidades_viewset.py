from django_filters import rest_framework as filters
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..serializers import UnidadeSerializer, UnidadeListSerializer
from ...models import Unidade
from ...choices.tipos_unidade import TIPOS_CHOICE
from ...services import monta_unidade_para_atribuicao
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter


class UnidadesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Unidade.objects.all().order_by("tipo_unidade", "nome")
    filter_backends = (filters.DjangoFilterBackend, SearchFilter,)
    filters = (filters.DjangoFilterBackend, SearchFilter,)
    serializer_class = UnidadeSerializer
    filterset_fields = ('tipo_unidade', 'codigo_eol', 'dre__uuid')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='tipo_unidade',
                description='Filtra unidades pelo tipo',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='codigo_eol',
                description='Filtra unidades pelo código EOL',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='tecnico',
                description='UUID do técnico responsável',
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='search',
                description='Busca por nome ou código EOL',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={200: UnidadeSerializer(many=True)},
        description="Lista unidades filtrando por tipo, código EOL, técnico ou busca textual."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = Unidade.objects.all()

        tipo_unidade = self.request.query_params.get('tipo_unidade')
        if tipo_unidade:
            qs = qs.filter(tipo_unidade=tipo_unidade)

        codigo_eol = self.request.query_params.get('codigo_eol')
        if codigo_eol:
            qs = qs.filter(codigo_eol=codigo_eol)

        tecnico = self.request.query_params.get('tecnico')
        if tecnico:
            qs = qs.filter(atribuicoes__tecnico__uuid=tecnico)

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(Q(codigo_eol=search) | Q(nome__unaccent__icontains=search))

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return UnidadeListSerializer
        else:
            return UnidadeSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='dre_uuid',
                description='UUID da DRE para filtrar unidades',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='periodo',
                description='UUID do Período para filtrar unidades',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        description=(
            "Retorna as unidades disponíveis para atribuição, filtradas por DRE e período."
            "Ambos os parâmetros (dre_uuid e periodo_uuid) são obrigatórios."
        ),
        summary="Listar unidades para atribuição"
    )
    @action(detail=False, url_path='para-atribuicao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def para_atribuicao(self, request, *args, **kwargs):
        dre_uuid = request.query_params.get('dre_uuid')
        periodo_uuid = request.query_params.get('periodo')

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo_uuid como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        list_unidades = monta_unidade_para_atribuicao(self.get_queryset(), dre_uuid, periodo_uuid)
        return Response(list_unidades)

    @action(detail=False, url_path='excludes', permission_classes=[IsAuthenticated & PermissaoApiUe],
            serializer_class=UnidadeListSerializer, methods=['post'])
    def excludes(self, request, *args, **kwargs):
        """
        Retorna lista de unidades, excluindo as que estiverem na lista de exclude_uuids.
        Considerado como Post para recebimento de lista de exclude (que pode ser grande).
        Recurso utilizado para componentização de Vinculo de Unidades (front), uma vez que o comportamento
        possa mudar de acordo com a instancia/Modelo Relacionado.

        Parâmetros:
            exclude_uuids (list): lista de uuids de unidades a serem excluídas
            pagination (dict): dicionário com page_size como chave e quantidade de unidades por página como valor
            Exemplo:
                {
                    exclude_uuids: ["uuid-1234", "uuid-5678"],
                    pagination: { page: 1, page_size: 10 },
                }

        Retorna:
            dict: dicionário com a lista de unidades e informações de paginação
        """
        from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
        exclude_uuids = request.data.get("exclude_uuids", [])
        filtros = request.data.get("filters", {})
        pagination = request.data.get("pagination", {})
        qs = Unidade.objects.all()
        if exclude_uuids:
            qs = qs.exclude(uuid__in=exclude_uuids)

        nome_eol = filtros.get('nome_ou_codigo')
        if nome_eol is not None:
            qs = qs.filter(Q(codigo_eol=nome_eol) | Q(nome__unaccent__icontains=nome_eol))

        dre_uuid = filtros.get('dre')
        if dre_uuid:
            qs = qs.filter(Q(dre__uuid=dre_uuid))

        tipo_unidade = filtros.get('tipo_unidade')
        print('tipo_unidade', tipo_unidade)
        if tipo_unidade:
            qs = qs.filter(Q(tipo_unidade=tipo_unidade))

        paginator = CustomPagination()
        paginator.page_size = pagination.get("page_size", 10)

        page = paginator.paginate_queryset(qs, request)
        serializer = UnidadeListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, url_path='tipos-unidades', permission_classes=[IsAuthenticated & PermissaoApiUe],
            serializer_class=UnidadeListSerializer, methods=['get'])
    def tipo_unidades(self, request, *args, **kwargs):
        tipos = [{'id': choice[0], 'nome': choice[1]} for choice in TIPOS_CHOICE]
        tipos_ordenados = sorted(tipos, key=lambda item: item['nome'])
        return Response(tipos_ordenados)
