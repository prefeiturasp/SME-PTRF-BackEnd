from drf_spectacular.utils import (
    extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse
)

DOCS = dict(
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

