from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    OpenApiExample,
    inline_serializer,
)

from ...serializers import OcupanteCargoSerializer


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

PARAM_RF = {
    "name": "rf",
    "description": "Registro funcional para consulta no SME Integração.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_CODIGO_EOL = {
    "name": "codigo-eol",
    "description": "Código EOL para consulta no SME Integração.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}


SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de ocupantes de cargos cadastrados no sistema.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Ocupantes de Cargos"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_PAGINATION),
    ],
    responses={
        200: OcupanteCargoSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um ocupante de cargo identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculos a unidades escolares UE, DRE ou SME podem acessar."
    ),
    tags=["Ocupantes de Cargos"],
    responses={
        200: OcupanteCargoSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No OcupanteCargo matches the given query."),
    },
)

SCHEMA_CONSULTA_CODIGO_IDENTIFICACAO_NO_SMEINTEGRACAO = extend_schema(
    description=(
        "Consulta dados no SME Integração usando `rf` ou `codigo-eol`.\n\n"
        "Pelo menos um dos parâmetros deve ser informado.\n\n"
        "- Com `rf`: retorna dados do servidor (usuário SGP).\n"
        "- Com `codigo-eol`: retorna dados do aluno."
    ),
    tags=["Ocupantes de Cargos"],
    parameters=[
        OpenApiParameter(**PARAM_RF),
        OpenApiParameter(**PARAM_CODIGO_EOL),
    ],
    examples=[
        OpenApiExample(
            name="Sucesso com rf",
            status_codes=[200],
            value={
                "cpf": "01078628831",
                "nome": "EDNA INES NATALI DEMETRIO",
                "codigoRf": "1391054",
                "email": "edna.demetrio@sme.prefeitura.sp.gov.br",
                "dreCodigo": None,
                "emailValido": True,
            },
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="ConsultaCodigoIdentificacaoSmeIntegracaoResponse",
                fields={
                    "cpf": serializers.CharField(required=False),
                    "nome": serializers.CharField(required=False),
                    "codigoRf": serializers.CharField(required=False),
                    "email": serializers.CharField(required=False),
                    "dreCodigo": serializers.CharField(allow_null=True, required=False),
                    "emailValido": serializers.BooleanField(required=False),
                },
            ),
            description="Consulta realizada com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos ou erro no SME Integração."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_GET_CARGOS_DO_RF_NO_SMEINTEGRACAO = extend_schema(
    description="Consulta os cargos de um RF no SME Integração.",
    tags=["Ocupantes de Cargos"],
    parameters=[
        OpenApiParameter(**PARAM_RF),
    ],
    examples=[
        OpenApiExample(
            name="Sucesso",
            status_codes=[200],
            value={
                "nomeServidor": "LUCIMARA CARDOSO RODRIGUES",
                "codigoServidor": "7210418",
                "cargos": [
                    {
                        "codigoCargo": "3298",
                        "nomeCargo": "PROF.ENS.FUND.II E MED.-PORTUGUES",
                        "nomeCargoSobreposto": "ASSISTENTE DE DIRETOR DE ESCOLA",
                        "codigoCargoSobreposto": "3085",
                    }
                ],
            },
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="GetCargosDoRfSmeIntegracaoResponse",
                fields={
                    "nomeServidor": serializers.CharField(required=False),
                    "codigoServidor": serializers.CharField(required=False),
                    "cargos": inline_serializer(
                        name="CargoDoRfSmeIntegracaoResponse",
                        many=True,
                        fields={
                            "codigoCargo": serializers.CharField(required=False),
                            "nomeCargo": serializers.CharField(required=False),
                            "nomeCargoSobreposto": serializers.CharField(required=False),
                            "codigoCargoSobreposto": serializers.CharField(required=False),
                        },
                    ),
                },
            ),
            description="Consulta realizada com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos ou erro no SME Integração."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)


DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    consulta_codigo_identificacao_no_smeintegracao=SCHEMA_CONSULTA_CODIGO_IDENTIFICACAO_NO_SMEINTEGRACAO,
    get_cargos_do_rf_no_smeintegracao=SCHEMA_GET_CARGOS_DO_RF_NO_SMEINTEGRACAO,
)
