from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers import CargoComposicaoSerializer, CargoComposicaoCreateSerializer


# ---------------------------------------------------------------------------
# Params
# ---------------------------------------------------------------------------

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página dentro do conjunto de resultados paginados.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de resultados a retornar por página.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGINATION = {
    "name": "pagination",
    "description": "Desabilitar paginação usando pagination=false (retorna todos os resultados).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_COMPOSICAO_UUID = {
    "name": "composicao_uuid",
    "description": "UUID da composição para filtrar os cargos associados.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao_uuid",
    "description": "UUID da associação para busca da composição vigente na data informada.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA = {
    "name": "data",
    "description": "Data de referência (formato YYYY-MM-DD) para localizar a composição vigente da associação.",
    "required": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de cargos de composições cadastrados no sistema.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_PAGINATION),
    ],
    responses={
        200: CargoComposicaoSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um cargo de composição identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    responses={
        200: CargoComposicaoSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No CargoComposicao matches the given query."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo cargo de composição.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    request=CargoComposicaoCreateSerializer,
    responses={
        201: CargoComposicaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos ou regras de negócio violadas."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um cargo de composição identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    request=CargoComposicaoCreateSerializer,
    responses={
        200: CargoComposicaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos ou regras de negócio violadas."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No CargoComposicao matches the given query."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um cargo de composição identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    request=CargoComposicaoCreateSerializer,
    responses={
        200: CargoComposicaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos ou regras de negócio violadas."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No CargoComposicao matches the given query."),
    },
)

SCHEMA_CARGOS_DA_COMPOSICAO = extend_schema(
    description=(
        "Retorna a lista de cargos de uma composição específica, ordenada por cargo da associação.\n\n"
        "O parâmetro `composicao_uuid` é obrigatório.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    parameters=[
        OpenApiParameter(**PARAM_COMPOSICAO_UUID),
    ],
    responses={
        200: CargoComposicaoSerializer(many=True),
        400: OpenApiResponse(description="Parâmetro composicao_uuid inválido ou composição não encontrada."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_CARGOS_DIRETORIA_EXECUTIVA = extend_schema(
    description=(
        "Retorna a lista de cargos da diretoria executiva disponíveis no sistema.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    responses={
        200: OpenApiResponse(description="Lista de cargos da diretoria executiva retornada com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_COMPOSICAO_POR_DATA = extend_schema(
    description=(
        "Retorna os ocupantes e cargos da composição vigente de uma associação em uma data específica.\n\n"
        "Os parâmetros `associacao_uuid` e `data` são obrigatórios.\n\n"
        "Quando há múltiplas composições para o mesmo período, retorna a composição mais recente.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Cargos de Composições"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_DATA),
    ],
    responses={
        200: OpenApiResponse(description="Ocupantes e cargos da composição vigente retornados com sucesso."),
        400: OpenApiResponse(description="Parâmetros inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Composição não encontrada para a associação e data informadas."),
    },
)


DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    update=SCHEMA_UPDATE,
    cargos_da_composicao=SCHEMA_CARGOS_DA_COMPOSICAO,
    cargos_diretoria_executiva=SCHEMA_CARGOS_DIRETORIA_EXECUTIVA,
    ocupantes_e_cargos_da_composicao_por_data=SCHEMA_COMPOSICAO_POR_DATA,
)
