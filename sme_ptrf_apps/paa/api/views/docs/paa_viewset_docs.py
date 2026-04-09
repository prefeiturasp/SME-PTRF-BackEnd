from drf_spectacular.utils import (
    extend_schema, OpenApiResponse, OpenApiTypes, OpenApiExample
)

DOCS = dict(
    iniciar_retificacao=extend_schema(
        summary="Iniciar retificação do PAA",
        description=(
            "Inicia o processo de retificação de um PAA já gerado.\n\n"
            "**Fluxo executado:**\n"
            "1. Gera um snapshot do estado atual do PAA e persiste na tabela `ReplicaPaa` "
            "(imutável — serve como backup para eventual rollback).\n"
            "2. Cria uma `AtaPaa` do tipo `RETIFICACAO` com a justificativa informada.\n\n"
            "**Regra:** Caso já exista uma réplica para o PAA, o snapshot existente é retornado "
            "sem alteração, garantindo que o histórico original seja preservado."
        ),
        tags=["PAA - Retificação"],
        request={
            'application/json': {
                'type': 'object',
                'required': ['justificativa'],
                'properties': {
                    'justificativa': {
                        'type': 'string',
                        'description': 'Justificativa obrigatória para a retificação do PAA.',
                        'example': 'Correção nos valores previstos de receita do PTRF após revisão contábil.',
                    }
                }
            }
        },
        responses={
            201: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'mensagem': {'type': 'string', 'example': 'Retificação iniciada com sucesso.'},
                        'paa_uuid': {'type': 'string', 'format': 'uuid'},
                    }
                },
                description='Retificação iniciada. Retorna o UUID do PAA.',
                examples=[
                    OpenApiExample(
                        name='Retificação iniciada',
                        value={
                            'mensagem': 'Retificação iniciada com sucesso.',
                            'paa_uuid': '3fa85f64-5717-4562-b3fc-2c963f66afa6',
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'erro': {'type': 'string'},
                        'mensagem': {'type': 'string'},
                    }
                },
                description=(
                    "Erro de validação ou falha ao iniciar a retificação.\n\n"
                    "Possíveis valores de `erro`:\n"
                    "- `parametro_requerido` — campo `justificativa` não informado.\n"
                    "- `erro_retificacao` — falha interna ao processar a retificação."
                ),
            ),
            401: OpenApiResponse(description="Credenciais de autenticação não fornecidas."),
            403: OpenApiResponse(description="Sem permissão para executar esta ação."),
            404: OpenApiResponse(description="PAA não encontrado."),
        },
    ),

    paa_retificacao=extend_schema(
        summary="Comparativo do PAA em retificação",
        description=(
            "Retorna os dados completos do PAA enriquecidos com o comparativo entre o estado atual "
            "e o snapshot armazenado na réplica no momento em que a retificação foi iniciada.\n\n"
            "O campo `alteracoes` permite ao frontend identificar, por seção e por UUID de registro, "
            "se o item foi **adicionado**, **modificado** ou **removido** em relação ao original.\n\n"
            "**Seções comparadas:** `texto_introducao`, `texto_conclusao`, `objetivos`, "
            "`receitas_ptrf`, `receitas_pdde`, `receitas_outros_recursos`, `prioridades`.\n\n"
            "Retorna `404` se nenhuma retificação foi iniciada para o PAA informado."
        ),
        tags=["PAA - Retificação"],
        responses={
            200: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'uuid': {'type': 'string', 'format': 'uuid'},
                        'associacao': {'type': 'string', 'format': 'uuid'},
                        'periodo_paa': {'type': 'integer'},
                        'status': {'type': 'string'},
                        'texto_introducao': {'type': 'string', 'nullable': True},
                        'texto_conclusao': {'type': 'string', 'nullable': True},
                        'alteracoes': {
                            'type': 'object',
                            'description': (
                                "Mapa de alterações por seção. Campos de texto simples "
                                "(`texto_introducao`, `texto_conclusao`) retornam `{anterior, atual}`. "
                                "Seções de registros (`objetivos`, `receitas_*`, `prioridades`) retornam "
                                "um mapa `{ <uuid>: { acao, ... } }` onde `acao` pode ser "
                                "`adicionado`, `modificado` ou `removido`."
                            ),
                            'example': {
                                'texto_introducao': {
                                    'anterior': 'Texto original.',
                                    'atual': 'Texto atualizado após revisão.',
                                },
                                'objetivos': {
                                    'uuid-abc': {'acao': 'adicionado', 'dados': {'nome': 'Novo objetivo'}},
                                    'uuid-xyz': {
                                        'acao': 'modificado',
                                        'anterior': {'nome': 'Objetivo antigo'},
                                        'atual': {'nome': 'Objetivo renomeado'},
                                    },
                                },
                                'receitas_ptrf': {
                                    'uuid-ptrf-1': {'acao': 'removido', 'dados': {
                                        'previsao_valor_capital': '0.00',
                                        'previsao_valor_custeio': '1000.00',
                                        'previsao_valor_livre': '0.00',
                                    }},
                                },
                            },
                        },
                    }
                },
                description='PAA com comparativo de alterações em relação ao snapshot da retificação.',
            ),
            401: OpenApiResponse(description="Credenciais de autenticação não fornecidas."),
            403: OpenApiResponse(description="Sem permissão para executar esta ação."),
            404: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'erro': {'type': 'string', 'example': 'sem_retificacao'},
                        'mensagem': {'type': 'string'},
                    }
                },
                description="PAA não encontrado ou nenhuma retificação iniciada para este PAA.",
            ),
        },
    ),
)
