from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers.despesa_serializer import (
    DespesaSerializer,
    DespesaCreateSerializer,
    DespesaListComRateiosSerializer,
)

# ---------------------------------------------------------------------------
# Parâmetros de filtro – lista
# ---------------------------------------------------------------------------

PARAM_SEARCH = {
    "name": "search",
    "description": "Busca por descrição de especificação de material/serviço (sem acento, parcial).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao__uuid",
    "description": "Filtra pelo UUID da associação.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_CPF_CNPJ_FORNECEDOR = {
    "name": "cpf_cnpj_fornecedor",
    "description": "Filtra pelo CPF ou CNPJ do fornecedor (valor exato).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_DOCUMENTO_UUID = {
    "name": "tipo_documento__uuid",
    "description": "Filtra pelo UUID do tipo de documento.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_DOCUMENTO_ID = {
    "name": "tipo_documento__id",
    "description": "Filtra pelo ID do tipo de documento.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_NUMERO_DOCUMENTO = {
    "name": "numero_documento",
    "description": "Filtra pelo número do documento (valor exato).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS = {
    "name": "status",
    "description": "Filtra pelo status da despesa.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_RATEIOS_TAG_UUID = {
    "name": "rateios__tag__uuid",
    "description": "Filtra despesas que possuam ao menos um rateio com a tag informada (UUID).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_RATEIOS_ACAO_ASSOCIACAO_UUID = {
    "name": "rateios__acao_associacao__uuid",
    "description": "Filtra despesas que possuam ao menos um rateio vinculado à ação-associação informada (UUID).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_APLICACAO_RECURSO = {
    "name": "aplicacao_recurso",
    "description": (
        "Filtra despesas que possuam ao menos um rateio com o tipo de aplicação de recurso informado "
        "(ex.: `CUSTEIO`, `CAPITAL`)."
    ),
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_FORNECEDOR = {
    "name": "fornecedor",
    "description": "Busca pelo nome do fornecedor ou pelo CPF/CNPJ (parcial, sem acento).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_RATEIOS_CONTA_ASSOCIACAO_UUID = {
    "name": "rateios__conta_associacao__uuid",
    "description": "Filtra despesas que possuam ao menos um rateio vinculado à conta-associação informada (UUID).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_INICIO = {
    "name": "data_inicio",
    "description": "Data de início do intervalo de filtragem por `data_documento` (formato `YYYY-MM-DD`).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_FIM = {
    "name": "data_fim",
    "description": "Data de fim do intervalo de filtragem por `data_documento` (formato `YYYY-MM-DD`).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO_UUID = {
    "name": "periodo__uuid",
    "description": (
        "Filtra despesas pela `data_transacao` dentro do intervalo de realização do período informado (UUID)."
    ),
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_FILTRO_VINCULO_ATIVIDADES = {
    "name": "filtro_vinculo_atividades",
    "description": "Lista de IDs de tags separados por vírgula para filtrar despesas por vínculo de atividades.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_FILTRO_INFORMACOES = {
    "name": "filtro_informacoes",
    "description": (
        "Lista de identificadores de informações separados por vírgula. "
        "Remove da listagem as despesas que NÃO possuem as tags informadas."
    ),
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

# ---------------------------------------------------------------------------
# Parâmetros de ordenação
# ---------------------------------------------------------------------------

PARAM_ORDENAR_POR_NUMERO_DO_DOCUMENTO = {
    "name": "ordenar_por_numero_do_documento",
    "description": "Ordena pelo número do documento. Valores aceitos: `crescente`, `decrescente`.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ORDENAR_POR_DATA_ESPECIFICACAO = {
    "name": "ordenar_por_data_especificacao",
    "description": "Ordena pela data do documento. Valores aceitos: `crescente`, `decrescente`.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ORDENAR_POR_VALOR = {
    "name": "ordenar_por_valor",
    "description": "Ordena pelo valor total da despesa. Valores aceitos: `crescente`, `decrescente`.",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ORDENAR_POR_IMPOSTO = {
    "name": "ordenar_por_imposto",
    "description": (
        "Quando `true`, agrupa cada despesa geradora imediatamente antes dos seus impostos, "
        "aplicando em seguida os demais critérios de ordenação solicitados."
    ),
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

# ---------------------------------------------------------------------------
# Parâmetros de paginação
# ---------------------------------------------------------------------------

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
    "description": "Quantidade de resultados a retornar por página (padrão: 10).",
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

# ---------------------------------------------------------------------------
# Schemas dos métodos CRUD
# ---------------------------------------------------------------------------

SCHEMA_LIST = extend_schema(
    description=(
        "Retorna a lista paginada de despesas ativas (excluindo status `INATIVO`), "
        "ordenada por padrão por `-data_documento`.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    parameters=[
        OpenApiParameter(**PARAM_SEARCH),
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_CPF_CNPJ_FORNECEDOR),
        OpenApiParameter(**PARAM_TIPO_DOCUMENTO_UUID),
        OpenApiParameter(**PARAM_TIPO_DOCUMENTO_ID),
        OpenApiParameter(**PARAM_NUMERO_DOCUMENTO),
        OpenApiParameter(**PARAM_STATUS),
        OpenApiParameter(**PARAM_RATEIOS_TAG_UUID),
        OpenApiParameter(**PARAM_RATEIOS_ACAO_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_APLICACAO_RECURSO),
        OpenApiParameter(**PARAM_FORNECEDOR),
        OpenApiParameter(**PARAM_RATEIOS_CONTA_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_DATA_INICIO),
        OpenApiParameter(**PARAM_DATA_FIM),
        OpenApiParameter(**PARAM_PERIODO_UUID),
        OpenApiParameter(**PARAM_FILTRO_VINCULO_ATIVIDADES),
        OpenApiParameter(**PARAM_FILTRO_INFORMACOES),
        OpenApiParameter(**PARAM_ORDENAR_POR_NUMERO_DO_DOCUMENTO),
        OpenApiParameter(**PARAM_ORDENAR_POR_DATA_ESPECIFICACAO),
        OpenApiParameter(**PARAM_ORDENAR_POR_VALOR),
        OpenApiParameter(**PARAM_ORDENAR_POR_IMPOSTO),
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
    ],
    responses={
        200: DespesaListComRateiosSerializer(many=True),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes completos de uma despesa identificada pelo UUID, "
        "incluindo rateios, impostos e motivos de pagamento antecipado.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    responses={
        200: DespesaSerializer,
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Despesa matches the given query."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria uma nova despesa com os rateios e impostos informados.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    request=DespesaCreateSerializer,
    responses={
        201: DespesaCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente uma despesa identificada pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    request=DespesaCreateSerializer,
    responses={
        200: DespesaCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Despesa matches the given query."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente uma despesa identificada pelo UUID.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    request=DespesaCreateSerializer,
    responses={
        200: DespesaCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Despesa matches the given query."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui ou inativa uma despesa identificada pelo UUID.\n\n"
        "Quando a despesa possui o flag `inativar_em_vez_de_excluir` ativo, ela é marcada como inativa "
        "em vez de ser removida fisicamente do banco de dados. "
        "Despesas com rateios vinculados a contas-associação inativas não podem ser excluídas.\n\n"
        "**Requer autenticação.** Apenas usuários com vínculo a unidades escolares (UE) podem acessar."
    ),
    tags=["Despesas"],
    responses={
        200: OpenApiResponse(description="Despesa inativada com sucesso."),
        204: OpenApiResponse(description="Despesa excluída com sucesso."),
        400: OpenApiResponse(description="Operação não permitida (conta inativa ou erro de integridade referencial)."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
        404: OpenApiResponse(description="No Despesa matches the given query."),
    },
)

# ---------------------------------------------------------------------------
# Schemas das actions customizadas
# ---------------------------------------------------------------------------

SCHEMA_TABELAS = extend_schema(
    description=(
        "Retorna tabelas de dados de apoio necessárias para o formulário de despesas de uma associação, "
        "incluindo tipos de aplicação de recurso, custeio, documento, transação, ações, contas e tags.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Despesas"],
    parameters=[
        OpenApiParameter(
            name="associacao_uuid",
            description="UUID da associação cujas tabelas de apoio serão retornadas.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "tipos_aplicacao_recurso": {"type": "object"},
                    "tipos_custeio": {"type": "object"},
                    "tipos_documento": {"type": "object"},
                    "tipos_transacao": {"type": "object"},
                    "acoes_associacao": {"type": "object"},
                    "contas_associacao": {"type": "object"},
                    "tags": {"type": "object"},
                },
            },
            description="Tabelas de apoio retornadas com sucesso.",
        ),
        400: OpenApiResponse(description="Parâmetro `associacao_uuid` é obrigatório."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_JA_LANCADA = extend_schema(
    description=(
        "Verifica se já existe uma despesa lançada para a combinação de tipo de documento, "
        "número de documento, CPF/CNPJ do fornecedor e associação informados. "
        "Útil para evitar lançamentos duplicados.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Despesas"],
    parameters=[
        OpenApiParameter(
            name="tipo_documento",
            description="ID do tipo de documento.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="numero_documento",
            description="Número do documento.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="cpf_cnpj_fornecedor",
            description="CPF ou CNPJ do fornecedor.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="associacao__uuid",
            description="UUID da associação.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="despesa_uuid",
            description=(
                "UUID da despesa que está sendo editada. "
                "Quando informado, é excluída da verificação de duplicidade."
            ),
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "despesa_ja_lancada": {"type": "boolean"},
                    "uuid_despesa": {"type": "string"},
                },
            },
            description="Resultado da verificação de duplicidade.",
        ),
        400: OpenApiResponse(description="Parâmetros obrigatórios ausentes."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_TAGS_INFORMACOES_LIST = extend_schema(
    description=(
        "Retorna a lista de tags de informações disponíveis para filtragem de despesas.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Despesas"],
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "nome": {"type": "string"},
                        "descricao": {"type": "string"},
                    },
                },
            },
            description="Lista de tags de informações retornada com sucesso.",
        ),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

SCHEMA_VALIDA_DATA_DA_DESPESA = extend_schema(
    description=(
        "Valida se a data informada é permitida para lançamento de despesa em uma associação. "
        "Retorna erro quando a associação está encerrada e a data é posterior ao encerramento.\n\n"
        "**Requer autenticação.** Usuários com permissão de leitura ou gravação podem acessar."
    ),
    tags=["Despesas"],
    parameters=[
        OpenApiParameter(
            name="data",
            description="Data da despesa a ser validada (formato `YYYY-MM-DD`).",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="associacao_uuid",
            description="UUID da associação para a qual a data será validada.",
            required=True,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "erro_data_da_despesa": {"type": "string"},
                    "data_de_encerramento": {"type": "string"},
                    "mensagem": {"type": "string"},
                    "status": {"type": "integer"},
                },
            },
            description="Resultado da validação da data da despesa.",
        ),
        400: OpenApiResponse(description="Parâmetros inválidos ou ausentes."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
        403: OpenApiResponse(description="You do not have permission to perform this action."),
    },
)

# ---------------------------------------------------------------------------
# Mapa de schemas para uso com @extend_schema_view
# ---------------------------------------------------------------------------

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    tabelas=SCHEMA_TABELAS,
    ja_lancada=SCHEMA_JA_LANCADA,
    tags_informacoes_list=SCHEMA_TAGS_INFORMACOES_LIST,
    valida_data_da_despesa=SCHEMA_VALIDA_DATA_DA_DESPESA,
)
