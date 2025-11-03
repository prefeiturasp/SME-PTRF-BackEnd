from ...serializers.comentario_analise_consolidado_dre_serializer import ComentarioAnaliseConsolidadoDRESerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiTypes

DOCS = dict(
    comentarios_nao_notificados_e_notificados=extend_schema(
        description=(
            "Retorna duas listas separadas: comentários **não notificados** (ordenados por `ordem`) "
            "e comentários **notificados** (ordenados por `notificado_em` descendente), "
            "referentes ao Consolidado DRE informado via parâmetro `consolidado_dre`."
        ),
        parameters=[
            OpenApiParameter(
                name="consolidado_dre",
                description="UUID do Consolidado DRE para buscar os comentários associados.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: ComentarioAnaliseConsolidadoDRESerializer(many=True),
        },
        examples=[
            OpenApiExample(
                'Resposta',
                value={
                    "comentarios_nao_notificados": ComentarioAnaliseConsolidadoDRESerializer(many=True).data,
                    "comentarios_notificados": ComentarioAnaliseConsolidadoDRESerializer(many=True).data,
                },
            )
        ]
    ),
    reordenar_comentarios=extend_schema(
        description=(
            "Recebe uma lista de UUIDs de comentários na nova ordem desejada "
            "e atualiza a sequência de exibição conforme informado."
        ),
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Requisição',
                value={
                    "comentarios_de_analise": ["UUID1", "UUID2", "UUID3"],
                },
            ),
            OpenApiExample(
                'Resposta',
                value={
                    'operacao': 'reordenar-comentarios',
                    'mensagem': 'Ordenação de mensagens concluída com sucesso.'
                },
            )
        ]
    ),
)
