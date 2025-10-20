from ...serializers import MotivoEstornoSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

DOCS = dict(
    list=extend_schema(
        description=(
            "Retorna a lista completa de motivos de estorno cadastrados no sistema. "
            "É possível aplicar um filtro opcional por nome do motivo, utilizando o parâmetro `motivo`."
        ),
        parameters=[
            OpenApiParameter(name="motivo", required=False, type=str,
                             description="Filtro opcional para buscar motivos contendo o texto informado."),
        ],
        responses={
            200: OpenApiResponse(
                response=MotivoEstornoSerializer,
                description="Lista de motivos de estorno retornada com sucesso."
            ),
        },
    ),
    destroy=extend_schema(
        description=(
            "Exclui um motivo de estorno, desde que não haja registros vinculados a ele. "
            "Caso existam vínculos, a operação é bloqueada e uma mensagem explicativa é retornada."
        ),
        responses={
            204: OpenApiResponse(description=""),
            400: OpenApiResponse(description=(
                'Esse motivo não pode ser excluído, pois existem estornos já cadastrados com o mesmo.'
            )),
        },
    ),
)