from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers import PrioridadePaaListSerializer

PARAM_ACAO_ASSOCIACAO_UUID = {
    "name": "acao_associacao__uuid",
    "description": "Filtrar por UUID da ação da associação.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAA_UUID = {
    "name": "paa__uuid",
    "description": "Filtrar por UUID do PAA.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_RECURSO = {
    "name": "recurso",
    "description": "Filtrar por recurso (ex: 'MUNICIPAL', 'ESTADUAL', etc.).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_PRIORIDADE = {
    "name": "prioridade",
    "description": "Filtrar por prioridade (0 para False, 1 para True).",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PROGRAMA_PDDE_UUID = {
    "name": "programa_pdde__uuid",
    "description": "Filtrar por UUID do programa PDDE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACAO_PDDE_UUID = {
    "name": "acao_pdde__uuid",
    "description": "Filtrar por UUID da ação PDDE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_APLICACAO = {
    "name": "tipo_aplicacao",
    "description": "Filtrar por tipo de aplicação (ex: 'CUSTEIO', 'CAPITAL').",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_DESPESA_CUSTEIO_UUID = {
    "name": "tipo_despesa_custeio__uuid",
    "description": "Filtrar por UUID do tipo de despesa de custeio.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ESPECIFICACAO_MATERIAL_UUID = {
    "name": "especificacao_material__uuid",
    "description": "Filtrar por UUID da especificação de material.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_OUTRO_RECURSO_UUID = {
    "name": "outro_recurso__uuid",
    "description": "Filtrar por UUID de outro recurso.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista completa de prioridades do PAA para relatórios, sem paginação.\n\n"
        "Permite filtros por diversos campos para personalizar os resultados.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA Relatório"],
    parameters=[
        OpenApiParameter(**PARAM_ACAO_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_PAA_UUID),
        OpenApiParameter(**PARAM_RECURSO),
        OpenApiParameter(**PARAM_PRIORIDADE),
        OpenApiParameter(**PARAM_PROGRAMA_PDDE_UUID),
        OpenApiParameter(**PARAM_ACAO_PDDE_UUID),
        OpenApiParameter(**PARAM_TIPO_APLICACAO),
        OpenApiParameter(**PARAM_TIPO_DESPESA_CUSTEIO_UUID),
        OpenApiParameter(**PARAM_ESPECIFICACAO_MATERIAL_UUID),
        OpenApiParameter(**PARAM_OUTRO_RECURSO_UUID),
    ],
    responses={
        200: PrioridadePaaListSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma prioridade do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA Relatório"],
    responses={
        200: PrioridadePaaListSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Prioridade não encontrada."),
    },
)

DOCS = {
    "list": SCHEMA_LIST,
    "retrieve": SCHEMA_RETRIEVE,
}
