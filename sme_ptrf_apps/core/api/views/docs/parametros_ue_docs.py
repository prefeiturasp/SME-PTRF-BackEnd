from drf_spectacular.utils import extend_schema, OpenApiExample

DOCS = dict(
    texto_pagina_valores_reprogramados=extend_schema(
        description=(
            "Retorna o texto configurado nos parâmetros do sistema referente à página de valores reprogramados "
            "para Unidades Educacionais (UE)."
        ),
        responses={200: "result"},
        examples=[
            OpenApiExample(
                'Exemplo de retorno',
                value={
                    "detail": "Texto informativo exibido na página de valores reprogramados das UEs."
                },
                response_only=True
            )
        ]
    ),
)
