from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiTypes


DOCS = dict(
    total_recursos=extend_schema(
        description=(
            "Retorna o valor total dos recursos próprios cadastrados após aplicar os mesmos filtros "
            "disponíveis na listagem padrão."
        ),
        parameters=[
            OpenApiParameter(
                name="associacao__uuid",
                description="Filtra os registros pelo UUID da associação vinculada.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Total de recursos próprios correspondente aos filtros informados.",
                response={
                    "type": "object",
                    "properties": {
                        "total": {
                            "type": "number",
                            "format": "decimal",
                            "nullable": True,
                            "description": "Somatório dos valores dos recursos próprios.",
                        }
                    },
                    "example": {"total": "2500.35"},
                },
            ),
        },
    ),
)
