from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.users.api.serializers import (
    AlteraEmailSerializer,
    RedefinirSenhaSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserRetrieveSerializer,
)

from sme_ptrf_apps.core.api.serializers.unidade_serializer import (
    UnidadeListSerializer,
)

GRUPO_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "nome": {"type": "string"},
        "descricao": {"type": "string"},
        "visao": {"type": "string"},
    },
}

VISAO_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "nome": {"type": "string"},
    },
}

USUARIO_STATUS_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "usuario_core_sso": {
            "type": "object",
        },
        "usuario_sig_escola": {
            "type": "object",
        },
        "validacao_username": {
            "type": "object",
        },
        "e_servidor_na_unidade": {
            "type": "boolean",
        },
    },
}

UNIDADES_PERMISSOES_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
}

PARAM_VISAO = {
    "name": "visao",
    "description": "Filtra usuários pela visão (`SME`, `DRE` ou `UE`).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_UNIDADE_UUID = {
    "name": "unidade_uuid",
    "description": "UUID da unidade utilizada para filtragem.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_GROUP_ID = {
    "name": "groups__id",
    "description": "Filtra usuários pelo ID do grupo.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_SEARCH = {
    "name": "search",
    "description": "Busca por nome do usuário (sem acento, parcial) ou username.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao_uuid",
    "description": "Filtra usuários vinculados à associação informada.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_USERNAME = {
    "name": "username",
    "description": "Filtra pelo username do usuário.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_SERVIDOR = {
    "name": "servidor",
    "description": "Filtra usuários servidores (`True` ou `False`).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_UNIDADE_NOME = {
    "name": "unidade_nome",
    "description": "Busca parcial pelo nome da unidade.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de itens por página.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna a lista paginada de usuários do sistema.\n\n"
        "Permite filtros por visão, grupo, unidade, associação, username e servidor.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    parameters=[
        OpenApiParameter(**PARAM_VISAO),
        OpenApiParameter(**PARAM_UNIDADE_UUID),
        OpenApiParameter(**PARAM_GROUP_ID),
        OpenApiParameter(**PARAM_SEARCH),
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_USERNAME),
        OpenApiParameter(**PARAM_SERVIDOR),
        OpenApiParameter(**PARAM_UNIDADE_NOME),
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
    ],
    responses={
        200: UserSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes completos de um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    responses={
        200: UserRetrieveSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo usuário no sistema.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    request=UserCreateSerializer,
    responses={
        201: UserCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    request=UserCreateSerializer,
    responses={
        200: UserCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    request=UserCreateSerializer,
    responses={
        200: UserCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um usuário do sistema.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    responses={
        204: OpenApiResponse(description="Usuário removido com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_ME = extend_schema(
    description=(
        "Retorna os dados do usuário autenticado.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    responses={
        200: UserSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)

SCHEMA_ALTERA_EMAIL = extend_schema(
    description=(
        "Atualiza o e-mail do usuário informado.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    request=AlteraEmailSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_ALTERA_SENHA = extend_schema(
    description=(
        "Atualiza a senha do usuário informado.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    request=RedefinirSenhaSerializer,
    responses={
        200: UserSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_GRUPOS = extend_schema(
    description=(
        "Retorna os grupos disponíveis para a visão informada (`SME`, `DRE` ou `UE`).\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    parameters=[
        OpenApiParameter(
            name="visao",
            description="Visão desejada (`SME`, `DRE` ou `UE`).",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": GRUPO_RESPONSE_SCHEMA,
            },
            description="Lista de grupos retornada com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetro inválido."),
    },
)

SCHEMA_CONSULTA_SERVIDOR_SGP = extend_schema(
    description=(
        "Consulta informações do servidor no SGP/CoreSSO.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    parameters=[
        OpenApiParameter(
            name="username",
            description="RF do servidor.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={"type": "object"},
            description="Dados retornados com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetro inválido."),
    },
)

SCHEMA_USUARIO_STATUS = extend_schema(
    description=(
        "Retorna informações do usuário no CoreSSO e Sig.Escola, "
        "incluindo validações e vínculos.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    parameters=[
        OpenApiParameter(
            name="username",
            description="Username/RF do usuário.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="servidor",
            description="Indica se o usuário é servidor.",
            required=False,
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="unidade",
            description="UUID da unidade.",
            required=False,
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=USUARIO_STATUS_RESPONSE_SCHEMA,
            description="Status retornado com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos."),
    },
)

SCHEMA_UNIDADES_E_PERMISSOES = extend_schema(
    description=(
        "Retorna as unidades e permissões do usuário na visão informada.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    parameters=[
        OpenApiParameter(
            name="unidade_logada_uuid",
            description="UUID da unidade logada.",
            required=False,
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=UNIDADES_PERMISSOES_RESPONSE_SCHEMA,
            description="Dados retornados com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos."),
        404: OpenApiResponse(description="Usuário ou unidade não encontrados."),
    },
)

SCHEMA_VISOES = extend_schema(
    description=(
        "Retorna todas as visões cadastradas no sistema.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": VISAO_RESPONSE_SCHEMA,
            },
            description="Lista de visões retornada com sucesso.",
        ),
        400: OpenApiResponse(description="Erro ao consultar visões."),
    },
)

SCHEMA_UNIDADES_EM_SUPORTE = extend_schema(
    description=(
        "Retorna unidades onde o usuário possui acesso de suporte ativo.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários"],
    responses={
        200: UnidadeListSerializer(many=True),
        400: OpenApiResponse(description="Usuário não encontrado."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    me=SCHEMA_ME,
    altera_email=SCHEMA_ALTERA_EMAIL,
    altera_senha=SCHEMA_ALTERA_SENHA,
    grupos=SCHEMA_GRUPOS,
    consulta_servidor_sgp=SCHEMA_CONSULTA_SERVIDOR_SGP,
    usuario_status=SCHEMA_USUARIO_STATUS,
    unidades_e_permissoes_na_visao=SCHEMA_UNIDADES_E_PERMISSOES,
    visoes=SCHEMA_VISOES,
    unidades_em_suporte=SCHEMA_UNIDADES_EM_SUPORTE,
)
