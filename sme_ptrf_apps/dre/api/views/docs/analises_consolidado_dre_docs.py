from ...serializers.analise_consolidado_dre_serializer import AnaliseConsolidadoDreRetriveSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample

DOCS = dict(
    list=extend_schema(
        description="Retorna uma lista paginada de todas as análises de consolidado DRE disponíveis.",
        tags=["Análises Consolidado DRE"],
        responses={
            200: AnaliseConsolidadoDreRetriveSerializer(many=True),
        }
    ),
    retrieve=extend_schema(
        description="Retorna os detalhes de uma análise de consolidado DRE específica pelo UUID.",
        tags=["Análises Consolidado DRE"],
        responses={
            200: AnaliseConsolidadoDreRetriveSerializer,
        }
    ),
    previa_relatorio_devolucao_acertos=extend_schema(
        description="Solicita a geração assíncrona de uma prévia do relatório de devolução para acertos.",
        tags=["Análises Consolidado DRE"],
        parameters=[
            OpenApiParameter(
                name='analise_consolidado_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID da análise de consolidado DRE'
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Arquivo na fila para processamento",
                examples=[
                    OpenApiExample(
                        'Sucesso',
                        value={'mensagem': 'Arquivo na fila para processamento.'}
                    )
                ]
            ),
        }
    ),
    status_info_relatorio_devolucao_acertos=extend_schema(
        description="Retorna informações sobre o status de geração do relatório de devolução para acertos.",
        tags=["Análises Consolidado DRE"],
        parameters=[
            OpenApiParameter(
                name='analise_consolidado_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID da análise de consolidado DRE'
            ),
        ],
        responses={
            200: OpenApiResponse('result'),
        },
        examples=[
            OpenApiExample(
                'response',
                value='Relatório sendo gerado'
            )
        ]
    ),
    download_documento_pdf_devolucao_acertos=extend_schema(
        description="Realiza o download do arquivo PDF do relatório de devolução para acertos.",
        tags=["Análises Consolidado DRE"],
        parameters=[
            OpenApiParameter(
                name='analise_consolidado_uuid',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID da análise de consolidado DRE'
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Arquivo PDF",
                response=OpenApiTypes.BINARY
            ),
            404: OpenApiResponse(
                description="Arquivo não encontrado",
            ),
            400: OpenApiResponse(description="Parâmetros inválidos"),
        },
    ),
)
