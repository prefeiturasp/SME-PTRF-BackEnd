from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer
from sme_ptrf_apps.paa.enums import TipoAtividadeEstatutariaEnum, TipoAnosAtividadeEstatutariaEnum
from sme_ptrf_apps.paa.choices import Mes
from sme_ptrf_apps.paa.models.atividade_estatutaria import StatusChoices

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

PARAM_NOME = {
    "name": "nome",
    "description": "Filtra pelo nome da atividade estatutária (case-insensitive).",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO = {
    "name": "tipo",
    "description": "Filtra pelo tipo de atividade estatutária.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(TipoAtividadeEstatutariaEnum.choices()),
}

PARAM_ANO = {
    "name": "ano",
    "description": "Filtra pelo ano da atividade estatutária.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(TipoAnosAtividadeEstatutariaEnum.choices()),
}

PARAM_MES = {
    "name": "mes",
    "description": "Filtra pelo mês da atividade estatutária.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(Mes.choices),
}

PARAM_STATUS = {
    "name": "status",
    "description": "Filtra pelo status da atividade estatutária.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
    "enum": list(StatusChoices.choices),
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de Atividades Estatutárias do PAA.\n\n"
        "Permite filtrar por **nome**, **tipo**, **ano**, **mês** e **status**."
    ),
    tags=["Atividade Estatutária PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_NOME),
        OpenApiParameter(**PARAM_TIPO),
        OpenApiParameter(**PARAM_ANO),
        OpenApiParameter(**PARAM_MES),
        OpenApiParameter(**PARAM_STATUS),
    ],
    responses={
        200: AtividadeEstatutariaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de uma Atividade Estatutária do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Atividade Estatutária PAA"],
    responses={
        200: AtividadeEstatutariaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Atividade estatutária não encontrada."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria uma nova Atividade Estatutária do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Atividade Estatutária PAA"],
    request=AtividadeEstatutariaSerializer,
    responses={
        201: AtividadeEstatutariaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente uma Atividade Estatutária do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Atividade Estatutária PAA"],
    request=AtividadeEstatutariaSerializer,
    responses={
        200: AtividadeEstatutariaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Atividade estatutária não encontrada."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui uma Atividade Estatutária do PAA identificada pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Atividade Estatutária PAA"],
    responses={
        204: OpenApiResponse(description="Atividade estatutária excluída com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Atividade estatutária não encontrada."),
    },
)

SCHEMA_TABELAS = extend_schema(
    description=(
        "Retorna os valores de tabela utilizados para filtro de Atividades Estatutárias no PAA.\n\n"
        "As tabelas incluem **status**, **ano**, **mês** e **tipo**."
    ),
    tags=["Atividade Estatutária PAA"],
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
    examples=[
        OpenApiExample(
            'Resposta',
            value={
                'status': StatusChoices.to_dict(),
                'ano': TipoAnosAtividadeEstatutariaEnum.to_dict(),
                'mes': Mes.to_dict(),
                'tipo': TipoAtividadeEstatutariaEnum.to_dict(),
            },
        ),
    ],
)

SCHEMA_ORDENAR = extend_schema(
    description=(
        "Atualiza a ordenação de uma Atividade Estatutária do PAA.\n\n"
        "É necessário informar o UUID de destino no corpo da requisição como `destino`."
    ),
    tags=["Atividade Estatutária PAA"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="UUID de destino não informado ou inválido."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Atividade estatutária não encontrada."),
    },
    examples=[
        OpenApiExample(
            'Requisição',
            value={
                'destino': 'uuid-do-destino',
            },
        ),
        OpenApiExample(
            'Resposta',
            value={
                'mensagem': 'Ordenação atualizada com sucesso.',
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
    ordenar=SCHEMA_ORDENAR,
)
