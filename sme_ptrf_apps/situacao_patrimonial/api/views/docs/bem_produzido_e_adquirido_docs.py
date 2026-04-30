from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.situacao_patrimonial.api.serializers import (
    BemProduzidoEAdquiridoSerializer,
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

PARAM_ASSOCIACAO = {
    "name": "associacao_uuid",
    "description": "UUID da associação (obrigatório).",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ESPECIFICACAO = {
    "name": "especificacao_bem",
    "description": "Filtra pela descrição do bem.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_FORNECEDOR = {
    "name": "fornecedor",
    "description": "Filtra pelo nome do fornecedor.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACAO = {
    "name": "acao_associacao_uuid",
    "description": "UUID da ação da associação.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_CONTA = {
    "name": "conta_associacao_uuid",
    "description": "UUID da conta da associação.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODOS = {
    "name": "periodos_uuid",
    "description": "Lista de UUIDs de períodos separados por vírgula.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_INICIO = {
    "name": "data_inicio",
    "description": "Data inicial (YYYY-MM-DD).",
    "required": False,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_FIM = {
    "name": "data_fim",
    "description": "Data final (YYYY-MM-DD).",
    "required": False,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_VISAO_DRE = {
    "name": "visao_dre",
    "description": "Se true, retorna apenas bens completos.",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

TAG = ["Situação Patrimonial - Bens Adquiridos e Produzidos"]

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista combinada de bens produzidos e adquiridos.\n\n"
        "Regras:\n"
        "- Bens produzidos (rascunho e completos) + bens adquiridos\n"
        "- Ordenação por data de aquisição (mais recente primeiro)\n"
        "- Rascunhos sempre aparecem no topo\n\n"
        "Permite diversos filtros.\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_ASSOCIACAO),
        OpenApiParameter(**PARAM_ESPECIFICACAO),
        OpenApiParameter(**PARAM_FORNECEDOR),
        OpenApiParameter(**PARAM_ACAO),
        OpenApiParameter(**PARAM_CONTA),
        OpenApiParameter(**PARAM_PERIODOS),
        OpenApiParameter(**PARAM_DATA_INICIO),
        OpenApiParameter(**PARAM_DATA_FIM),
        OpenApiParameter(**PARAM_VISAO_DRE),
    ],
    responses={
        200: BemProduzidoEAdquiridoSerializer(many=True),
        400: OpenApiResponse(description="Parâmetros inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="Sem permissão."),
    },
)

SCHEMA_EXPORTAR = extend_schema(
    description=(
        "Inicia exportação assíncrona dos bens adquiridos e produzidos.\n\n"
        "- Processado em background\n"
        "- Retorna um task_id para acompanhamento\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO),
        OpenApiParameter(**PARAM_ESPECIFICACAO),
        OpenApiParameter(**PARAM_FORNECEDOR),
        OpenApiParameter(**PARAM_ACAO),
        OpenApiParameter(**PARAM_CONTA),
        OpenApiParameter(**PARAM_PERIODOS),
        OpenApiParameter(**PARAM_DATA_INICIO),
        OpenApiParameter(**PARAM_DATA_FIM),
    ],
    responses={
        202: OpenApiResponse(description="Exportação iniciada."),
        400: OpenApiResponse(description="Parâmetros inválidos."),
        500: OpenApiResponse(description="Erro interno."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    exportar=SCHEMA_EXPORTAR,
)
