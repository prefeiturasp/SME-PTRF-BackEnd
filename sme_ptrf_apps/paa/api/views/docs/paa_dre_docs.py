from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
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
    "description": "Quantidade de resultados a retornar por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_NOME_ESCOLA = {
    "name": "nome_escola",
    "description": "Filtrar pelo nome da escola.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_CODIGO_EOL = {
    "name": "codigo_eol",
    "description": "Filtrar pelo código EOL da escola.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS = {
    "name": "status",
    "description": "Filtrar pelo status do processo do PAA.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TEM_DEVOLUCAO = {
    "name": "tem_devolucao",
    "description": "Filtrar PAAs com devolução pendente.",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_EXERCICIO = {
    "name": "exercicio",
    "description": "Filtrar pelo exercício do PAA.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}


SCHEMA_LIST = extend_schema(
    exclude=True,
)


SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna uma listagem paginada de PAAs vinculados a uma DRE.\n\n"
        "O UUID informado na URL deve corresponder à unidade DRE.\n\n"
        "Permite aplicar filtros por nome da escola, código EOL, status, "
        "exercício e devolução."
    ),
    tags=["PAA DRE"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_NOME_ESCOLA),
        OpenApiParameter(**PARAM_CODIGO_EOL),
        OpenApiParameter(**PARAM_STATUS),
        OpenApiParameter(**PARAM_TEM_DEVOLUCAO),
        OpenApiParameter(**PARAM_EXERCICIO),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Erro de validação dos filtros."),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(description="DRE não encontrada."),
    },
    examples=[
        OpenApiExample(
            "Resposta paginada",
            value={
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "uuid": "9f7d6a10-1111-2222-3333-abcdef123456",
                        "nome_escola": "EMEF Exemplo",
                        "codigo_eol": "123456",
                        "status": "EM_ANALISE",
                        "exercicio": 2025,
                        "tem_devolucao": False,
                    },
                    {
                        "uuid": "7c8d9e20-4444-5555-6666-fedcba654321",
                        "nome_escola": "CEI Modelo",
                        "codigo_eol": "654321",
                        "status": "DEVOLVIDO",
                        "exercicio": 2025,
                        "tem_devolucao": True,
                    },
                ],
            },
        ),
        OpenApiExample(
            "Erro de validação",
            value={
                "status": [
                    "Selecione uma opção válida."
                ]
            },
            response_only=True,
            status_codes=["400"],
        ),
    ],
)


SCHEMA_TABELAS = extend_schema(
    description=(
        "Retorna dados auxiliares para os filtros da listagem PAA DRE."
    ),
    tags=["PAA DRE"],
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(description="DRE não encontrada."),
    },
    examples=[
        OpenApiExample(
            "Resposta",
            value={
                "status_processo": [
                    {
                        "label": "Em análise",
                        "value": "EM_ANALISE",
                    },
                    {
                        "label": "Devolvido",
                        "value": "DEVOLVIDO",
                    },
                ],
                "exercicios": [2024, 2025],
            },
        ),
    ],
)


DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    tabelas=SCHEMA_TABELAS,
)
