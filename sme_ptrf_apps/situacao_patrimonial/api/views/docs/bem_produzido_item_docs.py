from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.situacao_patrimonial.api.serializers import (
    BemProduzidoItemSerializer,
    BemProduzidoItemCreateSerializer,
)


PARAM_PAGE = {
    "name": "page",
    "description": "Número da página dentro do conjunto de resultados paginados.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de resultados por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_SEARCH = {
    "name": "search",
    "description": "Busca textual nos campos indexados do item.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_BEM_PRODUZIDO_UUID = {
    "name": "bem_produzido__uuid",
    "description": "UUID do Bem Produzido para filtrar os itens.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de itens de bens produzidos.\n\n"
        "Permite filtro por `bem_produzido__uuid` e busca textual.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_SEARCH),
        OpenApiParameter(**PARAM_BEM_PRODUZIDO_UUID),
    ],
    responses={
        200: BemProduzidoItemSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um item de bem produzido identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    responses={
        200: BemProduzidoItemSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Item não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo item de bem produzido.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    request=BemProduzidoItemCreateSerializer,
    responses={
        201: BemProduzidoItemSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente um item de bem produzido.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    request=BemProduzidoItemCreateSerializer,
    responses={
        200: BemProduzidoItemSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Item não encontrado."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um item de bem produzido.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    request=BemProduzidoItemCreateSerializer,
    responses={
        200: BemProduzidoItemSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Item não encontrado."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um item de bem produzido.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Bem Produzido Item"],
    responses={
        204: OpenApiResponse(description="Item removido com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Item não encontrado."),
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
