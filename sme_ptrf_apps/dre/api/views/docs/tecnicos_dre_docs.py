from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers.tecnico_dre_serializer import (
    TecnicoDreCreateSerializer,
    TecnicoDreSerializer,
)

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de itens por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_DRE_UUID = {
    "name": "dre__uuid",
    "description": "UUID da DRE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_RF = {
    "name": "rf",
    "description": "RF do técnico.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TRANSFERIR_PARA = {
    "name": "transferir_para",
    "description": (
        "UUID do técnico que receberá as atribuições "
        "do técnico removido."
    ),
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Lista paginada de técnicos da DRE.\n\n"
        "Permite filtros por DRE e RF."
    ),
    tags=["Técnicos DRE"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_DRE_UUID),
        OpenApiParameter(**PARAM_RF),
    ],
    responses={
        200: TecnicoDreSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um técnico da DRE "
        "identificado pelo UUID."
    ),
    tags=["Técnicos DRE"],
    responses={
        200: TecnicoDreSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(
            description="Técnico DRE não encontrado."
        ),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo técnico da DRE.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Técnicos DRE"],
    request=TecnicoDreCreateSerializer,
    responses={
        201: TecnicoDreSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um técnico da DRE "
        "identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Técnicos DRE"],
    request=TecnicoDreCreateSerializer,
    responses={
        200: TecnicoDreSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(
            description="Técnico DRE não encontrado."
        ),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um técnico da DRE "
        "identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Técnicos DRE"],
    request=TecnicoDreCreateSerializer,
    responses={
        200: TecnicoDreSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(
            description="Técnico DRE não encontrado."
        ),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui um técnico da DRE identificado pelo UUID.\n\n"
        "Opcionalmente permite transferir as atribuições "
        "para outro técnico através do parâmetro "
        "`transferir_para`."
    ),
    tags=["Técnicos DRE"],
    parameters=[
        OpenApiParameter(**PARAM_TRANSFERIR_PARA),
    ],
    responses={
        204: OpenApiResponse(
            description="Técnico DRE excluído com sucesso."
        ),
        400: OpenApiResponse(
            description="UUID do técnico de transferência inválido."
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(
            description="Técnico DRE não encontrado."
        ),
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
