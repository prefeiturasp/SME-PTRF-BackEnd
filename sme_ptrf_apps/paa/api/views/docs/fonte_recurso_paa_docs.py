from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.fonte_recurso_paa_serializer import FonteRecursoPaaSerializer


# ---------------------------------------------------------------------------
# Params
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de fontes de recurso do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Fonte Recurso PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
    ],
    responses={
        200: FonteRecursoPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma fonte de recurso do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Fonte Recurso PAA"],
    responses={
        200: FonteRecursoPaaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Fonte de recurso não encontrada."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria uma nova fonte de recurso do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Fonte Recurso PAA"],
    request=FonteRecursoPaaSerializer,
    responses={
        201: FonteRecursoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente uma fonte de recurso do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Fonte Recurso PAA"],
    request=FonteRecursoPaaSerializer,
    responses={
        200: FonteRecursoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Fonte de recurso não encontrada."),
    },
)


# ---------------------------------------------------------------------------
# DOCS
# ---------------------------------------------------------------------------

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
)
