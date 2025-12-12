from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiTypes, OpenApiParameter, OpenApiExample
from ...serializers.falha_geracao_pc_serializer import FalhaGeracaoPcSerializer

DOCS = dict(
    list=extend_schema(
        description="Retorna uma lista paginada de todas as falhas de geração de prestação de contas.",
        tags=["Falhas Geração PC"],
        responses={
            200: FalhaGeracaoPcSerializer(many=True),
        }
    ),
    retrieve=extend_schema(
        description="Retorna os detalhes de uma falha de geração de PC específica pelo UUID.",
        tags=["Falhas Geração PC"],
        responses={
            200: FalhaGeracaoPcSerializer,
            404: OpenApiResponse(description="Falha não encontrada")
        }
    ),
    create=extend_schema(
        description="Cria um novo registro de falha de geração de prestação de contas.",
        tags=["Falhas Geração PC"],
        request=FalhaGeracaoPcSerializer,
        responses={
            201: FalhaGeracaoPcSerializer,
            400: OpenApiResponse(description="Dados inválidos")
        }
    ),
    update=extend_schema(
        description="Atualiza completamente um registro de falha de geração de PC.",
        tags=["Falhas Geração PC"],
        request=FalhaGeracaoPcSerializer,
        responses={
            200: FalhaGeracaoPcSerializer,
            400: OpenApiResponse(description="Dados inválidos"),
            404: OpenApiResponse(description="Falha não encontrada")
        }
    ),
    partial_update=extend_schema(
        description="Atualiza parcialmente um registro de falha de geração de PC.",
        tags=["Falhas Geração PC"],
        request=FalhaGeracaoPcSerializer,
        responses={
            200: FalhaGeracaoPcSerializer,
            400: OpenApiResponse(description="Dados inválidos"),
            404: OpenApiResponse(description="Falha não encontrada")
        }
    ),
    destroy=extend_schema(
        description="Exclui um registro de falha de geração de PC.",
        tags=["Falhas Geração PC"],
        responses={
            204: OpenApiResponse(description="Registro excluído com sucesso"),
            404: OpenApiResponse(description="Falha não encontrada")
        }
    ),
    info_registro_falha_geracao_pc=extend_schema(
        description="Retorna informações detalhadas de falha de geração de PC para uma associação.",
        tags=["Falhas Geração PC"],
        parameters=[
            OpenApiParameter(
                name='associacao',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID da associação'
            ),
        ],
        responses={
            200: "Informações de registro de falha",
        },
        examples=[
            OpenApiExample(
                'Exemplo de retorno',
                value=[{
                    "exibe_modal": True,
                    "excede_tentativas": False,
                    "periodo_referencia": "",
                    "periodo_uuid": "uuid-1234",
                    "periodo_data_final": "2023-12-01",
                    "periodo_data_inicio": "2023-01-01",
                    "associacao": "uuid-222",
                    "usuario": "username",
                }],
                response_only=True
            )
        ]
    ),
)
