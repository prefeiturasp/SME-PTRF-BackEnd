from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse
)

DOCS = dict(
    iniciar_ata=extend_schema(
        parameters=[
            OpenApiParameter(
                name='paa_uuid',
                description='UUID do PAA',
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'uuid': {'type': 'string', 'format': 'uuid'},
                        'nome': {'type': 'string'},
                        'alterado_em': {'type': 'string', 'format': 'date-time', 'nullable': True},
                    }
                },
                description='Retorna a ata PAA encontrada ou criada.'
            ),
            400: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'erro': {'type': 'string'},
                        'mensagem': {'type': 'string'}
                    }
                },
                description='Erro de validação ou objeto não encontrado.'
            ),
        },
        description=(
            "Busca a ata PAA do PAA informado. "
            "Se não existir, cria automaticamente uma nova ata PAA. "
            "Retorna AtaPaaLookUpSerializer para GET e AtaPaaSerializer para POST."
        ),
        summary="Buscar ou criar ata PAA"
    ),
    download_arquivo_ata_paa=extend_schema(
        parameters=[
            OpenApiParameter(
                name='ata-paa-uuid',
                description='UUID da ata PAA',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            (200, 'application/pdf'): OpenApiTypes.BINARY,
        },
        description="Retorna um arquivo PDF - Ata PAA."
    ),
    tabelas=extend_schema(
        parameters=[],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    "tipo_ata": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "tipos_reuniao": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "convocacoes": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                    "pareceres": {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {'id': {'type': 'string'}, 'nome': {'type': 'string'}}
                        },
                    },
                },
            }
        )},
    ),
)

