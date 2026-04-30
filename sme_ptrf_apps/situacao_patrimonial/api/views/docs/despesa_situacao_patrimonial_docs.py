from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.situacao_patrimonial.api.serializers import (
    DespesaSituacaoPatrimonialSerializer,
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
    "description": "Busca textual na descrição do material/serviço dos rateios.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_BEM_PRODUZIDO_UUID = {
    "name": "bem_produzido_uuid",
    "description": "UUID do bem produzido para excluir despesas já vinculadas a ele.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACAO_ASSOCIACAO = {
    "name": "rateios__acao_associacao__uuid",
    "description": "UUID da ação da associação para filtrar despesas.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_APLICACAO_RECURSO = {
    "name": "aplicacao_recurso",
    "description": "Filtra pelo tipo de aplicação do recurso nos rateios.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_FORNECEDOR = {
    "name": "fornecedor",
    "description": "Busca por nome, CPF ou CNPJ do fornecedor.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_CONTA_ASSOCIACAO = {
    "name": "rateios__conta_associacao__uuid",
    "description": "UUID da conta da associação vinculada ao rateio.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_INICIO = {
    "name": "data_inicio",
    "description": "Data inicial para filtro de data do documento (YYYY-MM-DD).",
    "required": False,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_FIM = {
    "name": "data_fim",
    "description": "Data final para filtro de data do documento (YYYY-MM-DD).",
    "required": False,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO = {
    "name": "periodo__uuid",
    "description": "UUID do período para filtrar despesas pela data de transação.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO = {
    "name": "associacao__uuid",
    "description": "UUID da associação vinculada à despesa.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_FILTRO_VINCULO_ATIVIDADES = {
    "name": "filtro_vinculo_atividades",
    "description": "Lista de IDs de tags (separados por vírgula) para filtrar vínculo com atividades.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de despesas disponíveis para vínculo com um bem produzido.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Despesa"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_SEARCH),
        OpenApiParameter(**PARAM_BEM_PRODUZIDO_UUID),
        OpenApiParameter(**PARAM_ACAO_ASSOCIACAO),
        OpenApiParameter(**PARAM_APLICACAO_RECURSO),
        OpenApiParameter(**PARAM_FORNECEDOR),
        OpenApiParameter(**PARAM_CONTA_ASSOCIACAO),
        OpenApiParameter(**PARAM_DATA_INICIO),
        OpenApiParameter(**PARAM_DATA_FIM),
        OpenApiParameter(**PARAM_PERIODO),
        OpenApiParameter(**PARAM_ASSOCIACAO),
        OpenApiParameter(**PARAM_FILTRO_VINCULO_ATIVIDADES),
    ],
    responses={
        200: DespesaSituacaoPatrimonialSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma despesa específica pelo UUID.\n\n"
        "Considera o contexto opcional de `bem_produzido_uuid`.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Situação Patrimonial - Despesa"],
    parameters=[
        OpenApiParameter(**PARAM_BEM_PRODUZIDO_UUID),
    ],
    responses={
        200: DespesaSituacaoPatrimonialSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Despesa não encontrada."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
)
