from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.outros_recursos_serializer import OutroRecursoSerializer

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

PARAM_NOME = {
    "name": "nome",
    "description": "Filtrar por nome do recurso (busca insensível a maiúsculas/minúsculas).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACEITA_CAPITAL = {
    "name": "aceita_capital",
    "description": "Filtrar por recursos que aceitam capital (true/false).",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACEITA_CUSTEIO = {
    "name": "aceita_custeio",
    "description": "Filtrar por recursos que aceitam custeio (true/false).",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACEITA_LIVRE_APLICACAO = {
    "name": "aceita_livre_aplicacao",
    "description": "Filtrar por recursos que aceitam livre aplicação (true/false).",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de outros recursos do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_NOME),
        OpenApiParameter(**PARAM_ACEITA_CAPITAL),
        OpenApiParameter(**PARAM_ACEITA_CUSTEIO),
        OpenApiParameter(**PARAM_ACEITA_LIVRE_APLICACAO),
    ],
    responses={
        200: OutroRecursoSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um outro recurso do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    responses={
        200: OutroRecursoSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Outro recurso não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo outro recurso do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    request=OutroRecursoSerializer,
    responses={
        201: OutroRecursoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um outro recurso do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    request=OutroRecursoSerializer,
    responses={
        200: OutroRecursoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Outro recurso não encontrado."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um outro recurso do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    request=OutroRecursoSerializer,
    responses={
        200: OutroRecursoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Outro recurso não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui um outro recurso do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Outros Recursos PAA"],
    responses={
        204: OpenApiResponse(description="Outro recurso excluído com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Outro recurso não encontrado."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
)
