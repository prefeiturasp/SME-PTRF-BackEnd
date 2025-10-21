from drf_spectacular.utils import extend_schema, OpenApiExample

DOCS = dict(
    texto_pagina_suporte=extend_schema(
        description=(
            "Retorna o texto configurado nos parâmetros do sistema referente à página de suporte SME "
        ),
        responses={200: "result"},
        examples=[
            OpenApiExample(
                'Exemplo de retorno',
                value={
                    "detail": "Texto informativo exibido na página de suporte SME."
                },
                response_only=True
            )
        ]
    ),
)