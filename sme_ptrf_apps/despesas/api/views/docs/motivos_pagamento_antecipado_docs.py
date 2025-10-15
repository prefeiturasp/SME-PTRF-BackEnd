from ...serializers.motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

DOCS = dict(
    list=extend_schema(
        description=(
            "Retorna a lista completa de motivos de pagamento antecipado cadastrados no sistema. "
            "É possível aplicar um filtro opcional por nome do motivo, utilizando o parâmetro `motivo`."
        ),
        parameters=[
            OpenApiParameter(name="motivo", required=False, type=str,
                             description="Filtro opcional para buscar motivos contendo o texto informado."),
        ],
        responses={
            200: OpenApiResponse(
                response=MotivoPagamentoAntecipadoSerializer,
                description="Lista de motivos de pagamento antecipado retornada com sucesso."
            ),
        },
    ),
    destroy=extend_schema(
        description=(
            "Exclui um motivo de pagamento antecipado, desde que não haja despesas vinculadas a ele. "
            "Caso existam vínculos, a operação é bloqueada e uma mensagem explicativa é retornada."
        ),
        responses={
            204: OpenApiResponse(description=""),
            400: OpenApiResponse(description=(
                'Essa operação não pode ser realizada. Há lançamentos '
                'cadastrados com esse motivo de pagamento antecipado.'
            )),
        },
    ),
)
