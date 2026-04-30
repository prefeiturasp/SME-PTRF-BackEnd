from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.situacao_patrimonial.api.serializers import (
    BemProduzidoSerializer,
    BemProduzidoSaveSerializer,
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

PARAM_ASSOCIACAO = {
    "name": "associacao_uuid",
    "description": "UUID da associação para filtrar os bens produzidos.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

TAG = ["Situação Patrimonial - Bem Produzido"]

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de bens produzidos.\n\n"
        "Permite filtro por associação.\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_ASSOCIACAO),
    ],
    responses={
        200: BemProduzidoSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description="Retorna os detalhes de um bem produzido.\n\n**Requer autenticação.**",
    tags=TAG,
    responses={
        200: BemProduzidoSerializer,
        404: OpenApiResponse(description="Não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description="Cria um novo bem produzido.\n\n**Requer autenticação.**",
    tags=TAG,
    request=BemProduzidoSaveSerializer,
    responses={
        201: BemProduzidoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description="Atualiza completamente um bem produzido.\n\n**Requer autenticação.**",
    tags=TAG,
    request=BemProduzidoSaveSerializer,
    responses={
        200: BemProduzidoSerializer,
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description="Atualiza parcialmente um bem produzido.\n\n**Requer autenticação.**",
    tags=TAG,
    request=BemProduzidoSaveSerializer,
    responses={
        200: BemProduzidoSerializer,
    },
)

SCHEMA_DESTROY = extend_schema(
    description="Remove um bem produzido.\n\n**Requer autenticação.**",
    tags=TAG,
    responses={
        204: OpenApiResponse(description="Removido com sucesso."),
    },
)

SCHEMA_EXCLUIR_LOTE = extend_schema(
    description=(
        "Remove em lote despesas vinculadas a um bem produzido.\n\n"
        "- Recebe uma lista de UUIDs de despesas.\n"
        "- Se o bem estiver COMPLETO, volta para RASCUNHO.\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "uuids": {
                    "type": "array",
                    "items": {"type": "string", "format": "uuid"},
                }
            },
            "required": ["uuids"],
        }
    },
    responses={
        200: OpenApiResponse(description="Despesas removidas com sucesso."),
        400: OpenApiResponse(description="Lista inválida."),
    },
)

SCHEMA_VERIFICAR_VALORES = extend_schema(
    description=(
        "Verifica se é permitido informar valores para as despesas.\n\n"
        "Regras:\n"
        "- Se todas as despesas forem de períodos finalizados com PC entregue → False\n"
        "- Caso contrário → True\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "uuids": {
                    "type": "array",
                    "items": {"type": "string", "format": "uuid"},
                }
            },
            "required": ["uuids"],
        }
    },
    responses={
        200: OpenApiResponse(description="Resultado da verificação."),
        400: OpenApiResponse(description="Lista inválida."),
    },
)

DOCS_BEM_PRODUZIDO = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    excluir_em_lote=SCHEMA_EXCLUIR_LOTE,
    verificar_se_pode_informar_valores=SCHEMA_VERIFICAR_VALORES,
)
