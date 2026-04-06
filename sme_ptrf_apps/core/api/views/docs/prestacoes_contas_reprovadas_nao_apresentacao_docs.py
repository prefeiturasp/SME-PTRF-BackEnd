from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers.prestacao_conta_reprovada_nao_apresentacao_serializer import (
    PrestacaoContaReprovadaNaoApresentacaoSerializer,
    PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
)

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

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao__uuid",
    "description": "Filtra pelo UUID da associação.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO_UUID = {
    "name": "periodo__uuid",
    "description": "Filtra pelo UUID do período.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}


SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista de prestações de contas reprovadas por não apresentação, "
        "ordenada por tipo de unidade e nome da unidade.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_PAGINATION),
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: PrestacaoContaReprovadaNaoApresentacaoSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma prestação de conta reprovada por não apresentação identificada pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    responses={
        200: PrestacaoContaReprovadaNaoApresentacaoSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No PrestacaoContaReprovadaNaoApresentacao matches the given query."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo registro de prestação de conta reprovada por não apresentação.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    request=PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
    responses={
        201: PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um registro de prestação de conta reprovada por não apresentação.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    request=PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
    responses={
        200: PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No PrestacaoContaReprovadaNaoApresentacao matches the given query."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um registro de prestação de conta reprovada por não apresentação.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    request=PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
    responses={
        200: PrestacaoContaReprovadaNaoApresentacaoCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No PrestacaoContaReprovadaNaoApresentacao matches the given query."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui um registro de prestação de conta reprovada por não apresentação.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares UE, DRE ou SME podem acessar.\n\n"
        "Disponível apenas quando a feature flag `pc-reprovada-nao-apresentacao` está habilitada."
    ),
    tags=["Prestações de Contas Reprovadas - Não Apresentação"],
    responses={
        204: OpenApiResponse(description="Registro excluído com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No PrestacaoContaReprovadaNaoApresentacao matches the given query."),
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
