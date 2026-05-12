from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices

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
    "description": "Filtra pelo nome do objetivo (case-insensitive).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS = {
    "name": "status",
    "description": "Filtra por Status (0 / 1).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(StatusChoices.choices),
}

PARAM_PAA_UUID = {
    "name": "paa__uuid",
    "description": "Filtra pelo UUID do PAA.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de Objetivos do PAA.\n\n"
        "Permite filtrar por **nome**, **status** e **paa__uuid**."
    ),
    tags=["Objetivo PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_NOME),
        OpenApiParameter(**PARAM_STATUS),
        OpenApiParameter(**PARAM_PAA_UUID),
    ],
    responses={
        200: ObjetivoPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um Objetivo do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Objetivo PAA"],
    responses={
        200: ObjetivoPaaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Objetivo não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo Objetivo do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Objetivo PAA"],
    request=ObjetivoPaaSerializer,
    responses={
        201: ObjetivoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um Objetivo do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Objetivo PAA"],
    request=ObjetivoPaaSerializer,
    responses={
        200: ObjetivoPaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Objetivo não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui um Objetivo do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Objetivo PAA"],
    responses={
        204: OpenApiResponse(description="Objetivo excluído com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Objetivo não encontrado."),
    },
)

SCHEMA_TABELAS = extend_schema(
    description=(
        "Retorna as tabelas de valores utilizadas para filtro de Objetivos do PAA.\n\n"
        "Retorna os valores possíveis para o campo **status**."
    ),
    tags=["Objetivo PAA"],
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
    examples=[
        OpenApiExample(
            'Resposta',
            value={
                'status': StatusChoices.to_dict(),
            },
        ),
    ],
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    tabelas=SCHEMA_TABELAS,
)
