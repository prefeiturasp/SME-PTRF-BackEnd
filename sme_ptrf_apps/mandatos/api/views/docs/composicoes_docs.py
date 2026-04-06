from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes
from ...serializers.composicao_serializer import ComposicaoSerializer

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página dentro do conjunto de resultados paginados.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de resultados a retornar por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGINATION = {
    "name": "pagination",
    "description": "Desabilitar paginação usando pagination=false (retorna todos os resultados).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de todas as composições de mandatos cadastradas no sistema.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Composições"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_PAGINATION),
    ],
    responses={
        200: ComposicaoSerializer(many=True),  # ✅ retorna os resultados paginados diretamente
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma composição de mandato específica identificada pelo UUID.\n\n"
        "Inclui informações sobre a associação, mandato, datas de vigência e composição anterior se houver.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Composições"],
    responses={
        200: ComposicaoSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Composicao matches the given query."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
)
