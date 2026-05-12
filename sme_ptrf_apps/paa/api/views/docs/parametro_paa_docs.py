from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from sme_ptrf_apps.paa.api.serializers.parametro_paa_serializer import ParametroPaaSerializer

SCHEMA_MES_ELABORACAO_PAA = extend_schema(
    description=(
        "Retorna o mês de elaboração do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["Parâmetros PAA"],
    responses={
        200: OpenApiResponse(
            description="Mês de elaboração do PAA.",
            examples=[
                {
                    "detail": "Janeiro"
                }
            ]
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_TEXTO_PAA_UE = extend_schema(
    description=(
        "Retorna textos específicos da PAA para UE.\n\n"
        "**Requer autenticação e permissão de leitura ou gravação.**"
    ),
    tags=["Parâmetros PAA"],
    responses={
        200: ParametroPaaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE_TEXTOS_PAA_UE = extend_schema(
    description=(
        "Atualiza textos específicos da PAA para UE.\n\n"
        "Permite atualizar um ou mais campos de texto do PAA. Todos os campos são opcionais.\n\n"
        "**Requer autenticação e permissão de gravação.**"
    ),
    tags=["Parâmetros PAA"],
    request=ParametroPaaSerializer,
    responses={
        200: OpenApiResponse(
            description="Textos atualizados com sucesso.",
            examples=[
                {
                    "detail": "Textos atualizados com sucesso"
                }
            ]
        ),
        400: OpenApiResponse(description="Dados inválidos ou nenhum campo enviado para atualização."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

DOCS = {
    "mes_elaboracao_paa": SCHEMA_MES_ELABORACAO_PAA,
    "texto_paa_ue": SCHEMA_TEXTO_PAA_UE,
    "update_textos_paa_ue": SCHEMA_UPDATE_TEXTOS_PAA_UE,
}
