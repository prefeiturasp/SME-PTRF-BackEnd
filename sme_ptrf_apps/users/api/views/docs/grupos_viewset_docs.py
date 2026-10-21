from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers import GrupoSerializer


PARAM_VISAO_BASE = {
    "name": "visao_base",
    "description": (
        'Visão base utilizada para filtragem dos grupos. '
        'Valores aceitos: `SME`, `DRE`, `UE`.\n\n'
        '- `SME`: retorna grupos de SME, DRE e UE.\n'
        '- `DRE`: retorna grupos de DRE e UE.\n'
        '- `UE`: retorna apenas grupos de UE.'
    ),
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_USERNAME = {
    "name": "username",
    "description": "Username do usuário.",
    "required": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_UUID_UNIDADE = {
    "name": "uuid_unidade",
    "description": (
        'UUID da unidade base utilizada na consulta. '
        'Também aceita o valor especial `SME`.'
    ),
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_SEARCH = {
    "name": "search",
    "description": "Busca textual por nome ou descrição do grupo.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_VISOES_ID = {
    "name": "visoes__id",
    "description": "Filtra grupos pelo ID da visão.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_VISOES_NOME = {
    "name": "visoes__nome",
    "description": "Filtra grupos pelo nome da visão (`SME`, `DRE`, `UE`).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ID_GRUPO = {
    "name": "id_grupo",
    "description": "ID do grupo de acesso.",
    "required": True,
    "type": OpenApiTypes.INT,
}

REQUEST_HABILITAR_GRUPO = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "id_grupo": {"type": "integer"},
    },
    "required": ["username", "id_grupo"],
}

REQUEST_DESABILITAR_GRUPO = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "id_grupo": {"type": "integer"},
    },
    "required": ["username", "id_grupo"],
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna a lista de grupos cadastrados no sistema.\n\n"
        "A listagem pode ser filtrada pela visão base (`SME`, `DRE` ou `UE`), "
        "incluindo apenas os grupos compatíveis com a visão informada.\n\n"
        "**Observação:** atualmente o endpoint permite acesso sem autenticação "
        "(`AllowAny`)."
    ),
    tags=["Grupos"],
    parameters=[
        OpenApiParameter(**PARAM_VISAO_BASE),
        OpenApiParameter(**PARAM_SEARCH),
        OpenApiParameter(**PARAM_VISOES_ID),
        OpenApiParameter(**PARAM_VISOES_NOME),
    ],
    responses={
        200: GrupoSerializer(many=True),
        400: OpenApiResponse(
            description="Valor inválido para o parâmetro `visao_base`."
        ),
    },
)

SCHEMA_GRUPOS_DISPONIVEIS_POR_ACESSO_VISAO = extend_schema(
    description=(
        "Retorna os grupos de acesso disponíveis para um usuário "
        "considerando a visão (`SME`, `DRE` ou `UE`) e a unidade base informada.\n\n"
        "O retorno informa também se o usuário já possui acesso ao grupo.\n\n"
        "**Observação:** atualmente o endpoint permite acesso sem autenticação "
        "(`AllowAny`)."
    ),
    tags=["Grupos"],
    parameters=[
        OpenApiParameter(**PARAM_USERNAME),
        OpenApiParameter(**PARAM_UUID_UNIDADE),
        OpenApiParameter(
            name="visao_base",
            description="Visão base da consulta.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=["SME", "DRE", "UE"],
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "grupo": {"type": "string"},
                        "descricao": {"type": "string"},
                        "possui_acesso": {"type": "boolean"},
                    },
                },
            },
            description="Lista de grupos disponíveis retornada com sucesso.",
        ),
        400: OpenApiResponse(
            description="Parâmetros inválidos ou visão inválida."
        ),
    },
)

SCHEMA_HABILITAR_GRUPO_ACESSO = extend_schema(
    description=(
        "Habilita um grupo de acesso para um usuário.\n\n"
        "O grupo informado será associado ao usuário.\n\n"
        "**Observação:** atualmente o endpoint permite acesso sem autenticação "
        "(`AllowAny`)."
    ),
    tags=["Grupos"],
    request=REQUEST_HABILITAR_GRUPO,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "mensagem": {"type": "string"},
                },
            },
            description="Grupo de acesso habilitado com sucesso.",
        ),
        400: OpenApiResponse(
            description="Dados inválidos ou grupo/usuário inexistente."
        ),
    },
)

SCHEMA_DESABILITAR_GRUPO_ACESSO = extend_schema(
    description=(
        "Desabilita um grupo de acesso de um usuário.\n\n"
        "O grupo informado será removido do usuário.\n\n"
        "**Observação:** atualmente o endpoint permite acesso sem autenticação "
        "(`AllowAny`)."
    ),
    tags=["Grupos"],
    request=REQUEST_DESABILITAR_GRUPO,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "mensagem": {"type": "string"},
                },
            },
            description="Grupo de acesso desabilitado com sucesso.",
        ),
        400: OpenApiResponse(
            description="Dados inválidos ou grupo/usuário inexistente."
        ),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    grupos_disponiveis_por_acesso_visao=SCHEMA_GRUPOS_DISPONIVEIS_POR_ACESSO_VISAO,
    habilitar_grupo_acesso=SCHEMA_HABILITAR_GRUPO_ACESSO,
    desabilitar_grupo_acesso=SCHEMA_DESABILITAR_GRUPO_ACESSO,
)
