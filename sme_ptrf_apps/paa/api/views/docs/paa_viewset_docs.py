from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    inline_serializer,
)
from rest_framework import serializers

from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaSerializer, PaaUpdateSerializer
from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import RecursoProprioPaaListSerializer
from sme_ptrf_apps.paa.api.serializers.receita_prevista_paa_serializer import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoRetrieveSerializer
from sme_ptrf_apps.paa.api.serializers.outros_recursos_periodo_paa_serializer import OutrosRecursosPeriodoPaaSerializer
from sme_ptrf_apps.paa.api.serializers.receita_prevista_outro_recurso_periodo_serializer import (
    ReceitaPrevistaOutroRecursoPeriodoSerializer)
from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer
from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_paa_serializer import AtividadeEstatutariaPaaSerializer

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página dentro do conjunto de resultados paginados.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de resultados a retornar por página.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGINATION = {
    "name": "pagination",
    "description": "Desabilitar paginação usando pagination=false (retorna todos os resultados).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao_uuid",
    "description": "UUID da associação para filtrar os PAAs.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID_REQUIRED = {
    "name": "associacao_uuid",
    "description": "UUID da associação. Obrigatório.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_CONFIRMAR = {
    "name": "confirmar",
    "description": "Confirmar importação: passar confirmar=1 para executar a importação efetiva.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna uma lista paginada de PAAs cadastrados no sistema.\n\n"
        "Pode ser filtrada pelo parâmetro `associacao_uuid`.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_PAGINATION),
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
    ],
    responses={
        200: PaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes de um PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    responses={
        200: PaaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um novo PAA.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    request=PaaSerializer,
    responses={
        201: PaaSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    request=PaaUpdateSerializer,
    responses={
        200: PaaUpdateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Remove um PAA identificado pelo UUID.\n\n"
        "Não é possível excluir um PAA que já está sendo utilizado na aplicação.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    responses={
        204: OpenApiResponse(description="PAA removido com sucesso."),
        400: OpenApiResponse(description="Este PAA não pode ser excluído porque já está sendo usado na aplicação."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_DOWNLOAD_LEVANTAMENTO_PRIORIDADES = extend_schema(
    description=(
        "Gera e retorna o PDF do levantamento de prioridades do PAA para a associação informada.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação em todas as unidades podem acessar."
    ),
    tags=["PAA"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
    ],
    responses={
        200: OpenApiResponse(description="Arquivo PDF retornado com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_DESATIVAR_ATUALIZACAO_SALDO = extend_schema(
    description=(
        "Congela (desativa a atualização automática) dos saldos das receitas previstas do PAA.\n\n"
        "Retorna a lista de receitas previstas com os saldos congelados.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação em todas as unidades podem acessar."
    ),
    tags=["PAA"],
    responses={
        200: ReceitaPrevistaPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_ATIVAR_ATUALIZACAO_SALDO = extend_schema(
    description=(
        "Descongela (reativa a atualização automática) dos saldos das receitas previstas do PAA.\n\n"
        "Não é permitido descongelar saldos após a geração do documento final do PAA.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação em todas as unidades podem acessar."
    ),
    tags=["PAA"],
    responses={
        200: ReceitaPrevistaPaaSerializer(many=True),
        400: OpenApiResponse(description="Não é possível descongelar saldos após a geração do documento final do PAA."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_RESUMO_PRIORIDADES = extend_schema(
    description=(
        "Retorna o resumo das prioridades do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(description="Resumo de prioridades retornado com sucesso."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_PAA_ANTERIORES = extend_schema(
    description=(
        "Retorna a lista de PAAs anteriores ao PAA identificado pelo UUID, ordenados "
        "do mais recente ao mais antigo.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação em todas as unidades podem acessar."
    ),
    tags=["PAA"],
    responses={
        200: PaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_PAA_VIGENTE_E_ANTERIORES = extend_schema(
    description=(
        "Retorna o PAA vigente e a lista de PAAs anteriores gerados para a associação informada.\n\n"
        "O campo `vigente` será `null` caso não exista PAA vigente.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a UE podem acessar."
    ),
    tags=["PAA"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID_REQUIRED),
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="PaaVigenteEAnterioresResponse",
                fields={
                    "vigente": PaaSerializer(allow_null=True),
                    "anteriores": PaaSerializer(many=True),
                },
            ),
            description="PAA vigente e PAAs anteriores retornados com sucesso.",
        ),
        400: OpenApiResponse(description="É necessário informar o uuid da associação."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="Associação ou período PAA vigente não encontrado."),
    },
)

SCHEMA_IMPORTAR_PRIORIDADES = extend_schema(
    description=(
        "Importa as prioridades de um PAA anterior para o PAA atual.\n\n"
        "Use `confirmar=1` para executar a importação efetiva. "
        "Sem o parâmetro, pode retornar uma mensagem de confirmação quando necessário.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação em todas as unidades podem acessar."
    ),
    tags=["PAA"],
    parameters=[
        OpenApiParameter(**PARAM_CONFIRMAR),
    ],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="ImportarPrioridadesResponse",
                fields={"mensagem": serializers.CharField()},
            ),
            description="Prioridades importadas com sucesso ou nenhuma prioridade encontrada.",
        ),
        400: OpenApiResponse(description="Erro de validação ou confirmação necessária."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="PAA atual ou PAA anterior não encontrado."),
    },
)

SCHEMA_RECEITAS_PREVISTAS = extend_schema(
    description=(
        "Retorna as ações PTRF da associação com suas receitas previstas no PAA.\n\n"
        "Cada item é um objeto `AcaoAssociacao` com o campo adicional `receitas_previstas_paa`, "
        "contendo a lista de receitas previstas vinculadas àquela ação no PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="AcaoAssociacaoComReceitasPrevistasPaaResponse",
                many=True,
                fields={
                    **{k: v for k, v in AcaoAssociacaoRetrieveSerializer().fields.items()},
                    "receitas_previstas_paa": ReceitaPrevistaPaaSerializer(many=True),
                },
            ),
            description="Lista de ações PTRF com receitas previstas retornada com sucesso.",
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_PLANO_ORCAMENTARIO = extend_schema(
    description=(
        "Retorna o plano orçamentário completo com dados formatados para o PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(description="Plano orçamentário retornado com sucesso."),
        400: OpenApiResponse(description="Erro ao processar plano orçamentário."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_OBJETIVOS_DISPONIVEIS = extend_schema(
    description=(
        "Retorna os objetivos disponíveis para o PAA identificado pelo UUID.\n\n"
        "Inclui objetivos globais (sem PAA associado) e objetivos específicos do PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: ObjetivoPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_ATIVIDADES_ESTATUTARIAS_DISPONIVEIS = extend_schema(
    description=(
        "Retorna as atividades estatutárias disponíveis para o PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: AtividadeEstatutariaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_ATIVIDADES_ESTATUTARIAS_PREVISTAS = extend_schema(
    description=(
        "Retorna as atividades estatutárias previstas do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: AtividadeEstatutariaPaaSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_RECURSOS_PROPRIOS_PREVISTOS = extend_schema(
    description=(
        "Retorna os recursos próprios previstos do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: RecursoProprioPaaListSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_OUTROS_RECURSOS_PERIODO = extend_schema(
    description=(
        "Retorna os outros recursos do período para o PAA identificado pelo UUID, "
        "com suas respectivas receitas previstas.\n\n"
        "Cada item é um objeto `OutroRecursoPeriodoPaa` com o campo adicional `receitas_previstas`, "
        "contendo a lista de receitas previstas vinculadas àquele recurso no PAA.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="OutroRecursosPeriodoComReceitasPrevistasPaaResponse",
                many=True,
                fields={
                    **{k: v for k, v in OutrosRecursosPeriodoPaaSerializer().fields.items()},
                    "receitas_previstas": ReceitaPrevistaOutroRecursoPeriodoSerializer(many=True),
                },
            ),
            description="Outros recursos do período com receitas previstas retornados com sucesso.",
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_GERAR_DOCUMENTO = extend_schema(
    description=(
        "Inicia a geração assíncrona do documento final do PAA identificado pelo UUID.\n\n"
        "É necessário passar `confirmar=1` no corpo da requisição para confirmar a geração.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    request=inline_serializer(
        name="GerarDocumentoRequest",
        fields={"confirmar": serializers.IntegerField(default=0)},
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="GerarDocumentoResponse",
                fields={"mensagem": serializers.CharField()},
            ),
            description="Geração de documento final iniciada.",
        ),
        400: OpenApiResponse(description="Geração não confirmada ou regras de negócio não atendidas."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_GERAR_PREVIA_DOCUMENTO = extend_schema(
    description=(
        "Inicia a geração assíncrona do documento prévio do PAA identificado pelo UUID.\n\n"
        "Não é possível gerar prévias após a geração do documento final.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="GerarPreviaDocumentoResponse",
                fields={"mensagem": serializers.CharField()},
            ),
            description="Geração de documento prévia iniciada.",
        ),
        400: OpenApiResponse(description="O documento final já foi gerado."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_DOCUMENTO_FINAL = extend_schema(
    description=(
        "Retorna o arquivo PDF do documento final do PAA identificado pelo UUID.\n\n"
        "Só é possível baixar o documento se ele já tiver sido gerado e concluído.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(description="Arquivo PDF do documento final retornado com sucesso."),
        400: OpenApiResponse(description="Documento final não gerado ou não concluído."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_DOCUMENTO_PREVIA = extend_schema(
    description=(
        "Retorna o arquivo PDF do documento prévio do PAA identificado pelo UUID.\n\n"
        "Só é possível baixar o documento se ele já tiver sido gerado e concluído.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(description="Arquivo PDF do documento prévio retornado com sucesso."),
        400: OpenApiResponse(description="Documento prévio não gerado ou não concluído."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_STATUS_GERACAO = extend_schema(
    description=(
        "Retorna o status de geração do documento (prévio ou final) do PAA identificado pelo UUID.\n\n"
        "**Requer autenticação.**"
    ),
    tags=["PAA"],
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="StatusGeracaoResponse",
                fields={
                    "mensagem": serializers.CharField(),
                    "versao": serializers.CharField(required=False),
                    "status": serializers.CharField(required=False),
                },
            ),
            description="Status de geração retornado com sucesso.",
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Paa matches the given query."),
    },
)

SCHEMA_INICIAR_RETIFICACAO = extend_schema(
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

SCHEMA_PAA_RETIFICACAO = extend_schema(
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

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    download_levantamento_prioridades_paa=SCHEMA_DOWNLOAD_LEVANTAMENTO_PRIORIDADES,
    desativar_atualizacao_saldo=SCHEMA_DESATIVAR_ATUALIZACAO_SALDO,
    ativar_atualizacao_saldo=SCHEMA_ATIVAR_ATUALIZACAO_SALDO,
    resumo_prioridades=SCHEMA_RESUMO_PRIORIDADES,
    paa_anteriores=SCHEMA_PAA_ANTERIORES,
    paa_vigente_e_anteriores=SCHEMA_PAA_VIGENTE_E_ANTERIORES,
    importar_prioridades=SCHEMA_IMPORTAR_PRIORIDADES,
    receitas_previstas=SCHEMA_RECEITAS_PREVISTAS,
    plano_orcamentario=SCHEMA_PLANO_ORCAMENTARIO,
    objetivos_disponiveis=SCHEMA_OBJETIVOS_DISPONIVEIS,
    atividades_estatutarias_disponiveis=SCHEMA_ATIVIDADES_ESTATUTARIAS_DISPONIVEIS,
    atividades_estatutarias_previstas=SCHEMA_ATIVIDADES_ESTATUTARIAS_PREVISTAS,
    recursos_proprios_previstos=SCHEMA_RECURSOS_PROPRIOS_PREVISTOS,
    outros_recursos_periodo=SCHEMA_OUTROS_RECURSOS_PERIODO,
    gerar_documento=SCHEMA_GERAR_DOCUMENTO,
    gerar_previa_documento=SCHEMA_GERAR_PREVIA_DOCUMENTO,
    documento_final=SCHEMA_DOCUMENTO_FINAL,
    documento_previa=SCHEMA_DOCUMENTO_PREVIA,
    satus_geracao=SCHEMA_STATUS_GERACAO,
    iniciar_retificacao=SCHEMA_INICIAR_RETIFICACAO,
    paa_retificacao=SCHEMA_PAA_RETIFICACAO,
)
