from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.prioridade_paa_serializer import (
    PrioridadePaaListSerializer,
    PrioridadePaaCreateUpdateSerializer,
)
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices

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

PARAM_ACAO_ASSOCIACAO_UUID = {
    "name": "acao_associacao__uuid",
    "description": "Filtrar pelo UUID da ação da associação.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAA_UUID = {
    "name": "paa__uuid",
    "description": "Filtrar pelo UUID do PAA.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_RECURSO = {
    "name": "recurso",
    "description": "Filtrar pelo tipo de recurso.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(RecursoOpcoesEnum.choices()),
}

PARAM_PRIORIDADE = {
    "name": "prioridade",
    "description": "Filtrar por prioridade (0/1).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(SimNaoChoices.choices),
}

PARAM_PROGRAMA_PDDE_UUID = {
    "name": "programa_pdde__uuid",
    "description": "Filtrar pelo UUID do programa PDDE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ACAO_PDDE_UUID = {
    "name": "acao_pdde__uuid",
    "description": "Filtrar pelo UUID da ação PDDE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_APLICACAO = {
    "name": "tipo_aplicacao",
    "description": "Filtrar pelo tipo de aplicação.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(TipoAplicacaoOpcoesEnum.choices()),
}

PARAM_TIPO_DESPESA_CUSTEIO_UUID = {
    "name": "tipo_despesa_custeio__uuid",
    "description": "Filtrar pelo UUID do tipo de despesa de custeio.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ESPECIFICACAO_MATERIAL_UUID = {
    "name": "especificacao_material__uuid",
    "description": "Filtrar pelo UUID da especificação de material/serviço.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAA_UUID_TABELAS = {
    "name": "paa__uuid",
    "description": "UUID do PAA para obter as tabelas.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de Prioridades do PAA.\n\n"
        "Permite filtrar por vários campos relacionados."
    ),
    tags=["Prioridade PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_ACAO_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_PAA_UUID),
        OpenApiParameter(**PARAM_RECURSO),
        OpenApiParameter(**PARAM_PRIORIDADE),
        OpenApiParameter(**PARAM_PROGRAMA_PDDE_UUID),
        OpenApiParameter(**PARAM_ACAO_PDDE_UUID),
        OpenApiParameter(**PARAM_TIPO_APLICACAO),
        OpenApiParameter(**PARAM_TIPO_DESPESA_CUSTEIO_UUID),
        OpenApiParameter(**PARAM_ESPECIFICACAO_MATERIAL_UUID),
    ],
    responses={
        200: PrioridadePaaListSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma Prioridade do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA"],
    responses={
        200: PrioridadePaaCreateUpdateSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Prioridade não encontrada."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria uma nova Prioridade do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA"],
    request=PrioridadePaaCreateUpdateSerializer,
    responses={
        201: PrioridadePaaCreateUpdateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente uma Prioridade do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA"],
    request=PrioridadePaaCreateUpdateSerializer,
    responses={
        200: PrioridadePaaCreateUpdateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Prioridade não encontrada."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui uma Prioridade do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Prioridade PAA"],
    responses={
        204: OpenApiResponse(description="Prioridade excluída com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Prioridade não encontrada."),
    },
)

SCHEMA_TABELAS = extend_schema(
    description=(
        "Retorna as tabelas de valores utilizadas para Prioridades do PAA.\n\n"
        "Inclui prioridades, recursos, tipos de aplicação e outros recursos baseados no PAA."
    ),
    tags=["Prioridade PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAA_UUID_TABELAS),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="PAA não identificado."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
    examples=[
        OpenApiExample(
            'Resposta',
            value={
                'prioridades': SimNaoChoices.to_dict(),
                'recursos': RecursoOpcoesEnum.to_dict(),
                'tipos_aplicacao': TipoAplicacaoOpcoesEnum.to_dict(),
                'outros_recursos': [
                    {'uuid': 'uuid-1', 'nome': 'Recurso 1'},
                    {'uuid': 'uuid-2', 'nome': 'Recurso 2'},
                ],
            },
        ),
    ],
)

SCHEMA_EXCLUIR_LOTE = extend_schema(
    description=(
        "Exclui em lote as Prioridades do PAA.\n\n"
        "Recebe uma lista de UUIDs das prioridades a serem excluídas."
    ),
    tags=["Prioridade PAA"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
    examples=[
        OpenApiExample(
            'Requisição',
            value={
                'lista_uuids': ['uuid-1', 'uuid-2'],
            },
        ),
        OpenApiExample(
            'Resposta',
            value={
                'mensagem': 'Prioridades excluídas com sucesso.',
                'erros': [],
            },
        ),
    ],
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    tabelas=SCHEMA_TABELAS,
    excluir_em_lote=SCHEMA_EXCLUIR_LOTE,
)
