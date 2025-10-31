from ...serializers.analise_documento_consolidado_dre_serializer import AnalisesDocumentosConsolidadoDreSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse


DOCS = dict(
    gravar_acerto=extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "analise_atual_consolidado": {"type": "string"},
                    "tipo_documento": {"type": "array", "items": {"type": "string"}},
                    "documento": {"type": "string"},
                    "detalhamento": {"type": "string"},
                },
                "required": [
                    "analise_atual_consolidado",
                    "tipo_documento",
                    "documento",
                    "detalhamento",
                ],
            }
        },
        responses={
            200: AnalisesDocumentosConsolidadoDreSerializer,
        },
    ),
    marcar_como_correto=extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "analise_atual_consolidado": {"type": "string"},
                    "documentos": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["analise_atual_consolidado", "documentos"],
            }
        },
        responses={
            200: OpenApiResponse(description="Documentos marcados como corretos."),
        },
    ),
    marcar_como_nao_conferido=extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "analise_atual_consolidado": {"type": "string"},
                    "uuids_analises_documentos": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["analise_atual_consolidado", "uuids_analises_documentos"],
            }
        },
        responses={
            200: OpenApiResponse(description="Documentos marcados como não conferidos."),
        },
    ),
    download_documento=extend_schema(
        parameters=[
            OpenApiParameter(
                name="documento_uuid",
                description="UUID do documento a ser baixado.",
                required=True,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="tipo_documento",
                description="Tipo de documento.",
                enum=['RELATORIO_CONSOLIDADO', 'ATA_PARECER_TECNICO'],
                required=True,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={(200, 'application/pdf'): OpenApiTypes.BINARY},
    ),
)
