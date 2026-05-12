from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.users.api.serializers import (
    UsuarioSerializer,
    UsuarioRetrieveSerializer,
    UsuarioCreateSerializer,
)

from sme_ptrf_apps.core.api.serializers import UnidadeListSerializer

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
        "info_membro_nao_servidor": {
            "type": "object",
        },
        "pode_acessar_unidade": {
            "type": "object",
            "properties": {
                "visao_base": {"type": "string"},
                "unidade": {"type": "string"},
                "pode_acessar": {"type": "boolean"},
                "mensagem": {"type": "string"},
                "info_exercicio": {"type": "object"},
            },
        },
    },
}

UNIDADES_USUARIO_RESPONSE_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": True,
    },
}

ACESSO_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "string"},
    },
}

PARAM_UUID_UNIDADE_BASE = {
    "name": "uuid_unidade_base",
    "description": (
        'UUID da unidade base ou valor `"SME"`.\n\n'
        "Quando informado:\n"
        "- SME: retorna todos os usuários.\n"
        "- UUID de DRE: retorna usuários da DRE e subordinadas.\n"
        "- UUID de UE: retorna apenas usuários da unidade."
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

PARAM_E_SERVIDOR = {
    "name": "e_servidor",
    "description": 'Indica se o usuário é servidor (`True` ou `False`).',
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_UUID_UNIDADE = {
    "name": "uuid_unidade",
    "description": 'UUID da unidade ou valor `"SME"`.',
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_VISAO_BASE = {
    "name": "visao_base",
    "description": "Visão base utilizada na consulta.",
    "required": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": ["SME", "DRE", "UE"],
}

PARAM_SEARCH = {
    "name": "search",
    "description": "Busca pelo código EOL ou nome da unidade.",
    "required": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna a lista paginada de usuários.\n\n"
        "A listagem considera a unidade base informada:\n"
        "- `SME`: todos os usuários.\n"
        "- `DRE`: usuários da DRE e subordinadas.\n"
        "- `UE`: usuários da unidade.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    parameters=[
        OpenApiParameter(**PARAM_UUID_UNIDADE_BASE),
    ],
    responses={
        200: UsuarioSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes completos de um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    responses={
        200: UsuarioRetrieveSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request=UsuarioCreateSerializer,
    responses={
        201: UsuarioCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request=UsuarioCreateSerializer,
    responses={
        200: UsuarioCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request=UsuarioCreateSerializer,
    responses={
        200: UsuarioCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    responses={
        204: OpenApiResponse(description="Usuário removido com sucesso."),
        404: OpenApiResponse(description="Usuário não encontrado."),
    },
)

SCHEMA_CONSULTA_SERVIDOR_SGP = extend_schema(
    description=(
        "Consulta informações do usuário no SGP/CoreSSO.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    parameters=[
        OpenApiParameter(**PARAM_USERNAME),
    ],
    responses={
        200: OpenApiResponse(
            response={"type": "object"},
            description="Informações retornadas com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetro username obrigatório."),
    },
)

SCHEMA_USUARIO_STATUS = extend_schema(
    description=(
        "Retorna informações completas do usuário no CoreSSO e Sig.Escola, "
        "incluindo validações de acesso, vínculos e permissões.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    parameters=[
        OpenApiParameter(**PARAM_USERNAME),
        OpenApiParameter(**PARAM_E_SERVIDOR),
        OpenApiParameter(**PARAM_UUID_UNIDADE),
    ],
    responses={
        200: OpenApiResponse(
            response=USUARIO_STATUS_RESPONSE_SCHEMA,
            description="Status do usuário retornado com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos."),
    },
)

SCHEMA_REMOVER_ACESSOS = extend_schema(
    description=(
        "Remove os acessos do usuário para a unidade base e subordinadas.\n\n"
        "Comportamento:\n"
        "- `SME`: remove todos os acessos.\n"
        "- `DRE`: remove acessos da DRE e subordinadas.\n"
        "- `UE`: remove apenas o acesso da unidade.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request=None,
    responses={
        204: OpenApiResponse(description="Acessos removidos com sucesso."),
        400: OpenApiResponse(description="Parâmetros inválidos."),
        500: OpenApiResponse(description="Erro interno ao remover acessos."),
    },
)

SCHEMA_UNIDADES_DO_USUARIO = extend_schema(
    description=(
        "Retorna a lista de unidades disponíveis para o usuário "
        "considerando a visão base informada.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    parameters=[
        OpenApiParameter(**PARAM_USERNAME),
        OpenApiParameter(**PARAM_UUID_UNIDADE),
        OpenApiParameter(**PARAM_VISAO_BASE),
    ],
    responses={
        200: OpenApiResponse(
            response=UNIDADES_USUARIO_RESPONSE_SCHEMA,
            description="Lista de unidades retornada com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos."),
    },
)

SCHEMA_HABILITAR_ACESSO = extend_schema(
    description=(
        "Habilita acesso do usuário para a unidade informada.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "uuid_unidade": {"type": "string"},
            },
            "required": ["username", "uuid_unidade"],
        }
    },
    responses={
        200: OpenApiResponse(
            response=ACESSO_RESPONSE_SCHEMA,
            description="Acesso habilitado com sucesso.",
        ),
        400: OpenApiResponse(description="Payload inválido."),
    },
)

SCHEMA_DESABILITAR_ACESSO = extend_schema(
    description=(
        "Desabilita acesso do usuário para a unidade informada.\n\n"
        "Também remove grupos de acesso relacionados à unidade.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "uuid_unidade": {"type": "string"},
                "visao_base": {"type": "string"},
                "acesso_concedido_sme": {"type": "boolean"},
            },
            "required": ["username", "uuid_unidade", "visao_base"],
        }
    },
    responses={
        200: OpenApiResponse(
            response=ACESSO_RESPONSE_SCHEMA,
            description="Acesso desabilitado com sucesso.",
        ),
        400: OpenApiResponse(description="Payload inválido."),
    },
)

SCHEMA_UNIDADES_DISPONIVEIS = extend_schema(
    description=(
        "Retorna lista paginada de unidades disponíveis para inclusão "
        "de vínculo ao usuário.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    parameters=[
        OpenApiParameter(**PARAM_USERNAME),
        OpenApiParameter(**PARAM_SEARCH),
    ],
    responses={
        200: UnidadeListSerializer(many=True),
        400: OpenApiResponse(description="Parâmetros inválidos."),
    },
)

SCHEMA_INCLUIR_UNIDADE = extend_schema(
    description=(
        "Inclui vínculo do usuário com a unidade informada.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Usuários V2"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "uuid_unidade": {"type": "string"},
            },
            "required": ["username", "uuid_unidade"],
        }
    },
    responses={
        201: OpenApiResponse(
            response=ACESSO_RESPONSE_SCHEMA,
            description="Unidade incluída com sucesso.",
        ),
        400: OpenApiResponse(description="Payload inválido."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    consulta_servidor_sgp=SCHEMA_CONSULTA_SERVIDOR_SGP,
    usuario_status=SCHEMA_USUARIO_STATUS,
    remover_acessos=SCHEMA_REMOVER_ACESSOS,
    unidades_do_usuario=SCHEMA_UNIDADES_DO_USUARIO,
    habilitar_acesso=SCHEMA_HABILITAR_ACESSO,
    desabilitar_acesso=SCHEMA_DESABILITAR_ACESSO,
    unidades_disponiveis_para_inclusao=SCHEMA_UNIDADES_DISPONIVEIS,
    incluir_unidade=SCHEMA_INCLUIR_UNIDADE,
)
