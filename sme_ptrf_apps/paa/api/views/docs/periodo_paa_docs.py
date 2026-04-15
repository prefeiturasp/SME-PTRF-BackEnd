from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.periodo_paa_serializer import PeriodoPaaSerializer


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

PARAM_REFERENCIA = {
    "name": "referencia",
    "description": (
        "Filtra os períodos pelo campo referência (busca parcial, ignorando acentuação)."
    ),
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_OUTRO_RECURSO = {
    "name": "outro_recurso",
    "description": (
        "UUID do outro recurso para filtrar os períodos que possuem vínculo ativo com ele."
    ),
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de períodos de PAA.\n\n"
        "Os resultados são ordenados por `data_inicial` (decrescente) e `referencia`.\n\n"
        "Inclui o campo adicional `qtd_outros_recursos_habilitados`, representando a quantidade "
        "de outros recursos ativos vinculados ao período.\n\n"
        "Permite filtrar por referência e por outro recurso vinculado.\n\n"
        "**Requer autenticação.** Apenas usuários SME com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Período PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_REFERENCIA),
        OpenApiParameter(**PARAM_OUTRO_RECURSO),
    ],
    responses={
        200: PeriodoPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Você não tem permissão para acessar este recurso."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um período de PAA identificado pelo UUID.\n\n"
        "Inclui o campo `qtd_outros_recursos_habilitados`.\n\n"
        "**Requer autenticação.** Apenas usuários SME com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Período PAA"],
    responses={
        200: PeriodoPaaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Você não tem permissão para acessar este recurso."),
        404: OpenApiResponse(description="Período não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo período de PAA.\n\n"
        "**Requer autenticação.** Apenas usuários SME com permissão de gravação podem acessar."
    ),
    tags=["Período PAA"],
    request=PeriodoPaaSerializer,
    responses={
        201: PeriodoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Você não tem permissão para executar esta ação."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um período de PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários SME com permissão de gravação podem acessar."
    ),
    tags=["Período PAA"],
    request=PeriodoPaaSerializer,
    responses={
        200: PeriodoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Você não tem permissão para executar esta ação."),
        404: OpenApiResponse(description="Período não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um período de PAA identificado pelo UUID.\n\n"
        "Não é possível excluir o período nas seguintes situações:\n"
        "- Quando existir um PAA vinculado ao período\n"
        "- Quando houver vínculos com 'Outro Recurso'\n\n"
        "**Requer autenticação.** Apenas usuários SME com permissão de gravação podem acessar."
    ),
    tags=["Período PAA"],
    responses={
        204: OpenApiResponse(description="Período removido com sucesso."),
        400: OpenApiResponse(
            description=(
                "Não foi possível excluir o período.\n\n"
                "- Período vinculado a um PAA\n"
                "- Período com vínculos de 'Outro Recurso'\n"
                "- Erro inesperado"
            )
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Você não tem permissão para executar esta ação."),
        404: OpenApiResponse(description="Período não encontrado."),
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
)
