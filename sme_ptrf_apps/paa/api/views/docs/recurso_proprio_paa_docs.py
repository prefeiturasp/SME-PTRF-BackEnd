from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import (
    RecursoProprioPaaCreateSerializer,
    RecursoProprioPaaListSerializer,
)

# ---------------------------------------------------------------------------
# Params
# ---------------------------------------------------------------------------

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página dentro do conjunto paginado.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de registros por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao__uuid",
    "description": "UUID da associação para filtro.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAA_UUID = {
    "name": "paa__uuid",
    "description": "UUID do PAA para filtro.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_CONFIRMAR_LIMPEZA = {
    "name": "confirmar_limpeza_prioridades_paa",
    "description": (
        "Confirma a limpeza das prioridades impactadas ao excluir o recurso.\n\n"
        "Use `true` para confirmar a operação."
    ),
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de recursos próprios do PAA.\n\n"
        "Permite filtrar por associação e PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_PAA_UUID),
    ],
    responses={
        200: RecursoProprioPaaListSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um recurso próprio do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    responses={
        200: RecursoProprioPaaListSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Recurso não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo recurso próprio para o PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    request=RecursoProprioPaaCreateSerializer,
    responses={
        201: RecursoProprioPaaListSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um recurso próprio identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    request=RecursoProprioPaaCreateSerializer,
    responses={
        200: RecursoProprioPaaListSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Recurso não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um recurso próprio do PAA.\n\n"
        "Caso existam prioridades impactadas, será necessário confirmar a limpeza "
        "utilizando o parâmetro `confirmar_limpeza_prioridades_paa=true`.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    parameters=[
        OpenApiParameter(**PARAM_CONFIRMAR_LIMPEZA),
    ],
    responses={
        204: OpenApiResponse(description="Recurso removido com sucesso."),
        400: OpenApiResponse(
            description=(
                "Erro ao excluir recurso.\n\n"
                "- Confirmação necessária para limpar prioridades\n"
                "- Recurso possui vínculos (ProtectedError)\n"
                "- Falha ao processar regras de negócio"
            )
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Recurso não encontrado."),
    },
)

SCHEMA_TOTAL_RECURSOS = extend_schema(
    description=(
        "Retorna o valor total dos recursos próprios cadastrados.\n\n"
        "Aplica os mesmos filtros da listagem.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Recurso Próprio PAA"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_PAA_UUID),
    ],
    responses={
        200: OpenApiResponse(
            description="Total de recursos próprios correspondente aos filtros informados.",
            response={
                "type": "object",
                "properties": {
                    "total": {
                        "type": "number",
                        "format": "decimal",
                        "nullable": True,
                        "description": "Somatório dos valores dos recursos próprios.",
                    }
                },
                "example": {"total": "2500.35"},
            },
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
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
    destroy=SCHEMA_DESTROY,
    total_recursos=SCHEMA_TOTAL_RECURSOS,
)
