from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

PARAM_DATA_INICIAL = {
    "name": 'data_inicio',
    "description": 'Filtro de início de data de criação',
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_FINAL = {
    "name": 'data_final',
    "description": 'Filtro de fim de data de criação',
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_DRE_UUI = {
    "name": 'dre_uui',
    "description": 'Filtro de uuid de DRE',
    "required": False,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

RESPONSE_DEFAULT = {
    "name": 'Response',
    "value": {
        "response": "O arquivo está sendo gerado e será enviado para a central de download após conclusão."
    },
}

SCHEMA_DEFAULT = extend_schema(
    parameters=[
        OpenApiParameter(**PARAM_DATA_INICIAL),
        OpenApiParameter(**PARAM_DATA_FINAL),
        OpenApiParameter(**PARAM_DRE_UUI),
    ],
    responses={201: "result"},
    examples=[OpenApiExample(**RESPONSE_DEFAULT)]
)

SCHEMA_ONLY_DATES = extend_schema(
    parameters=[
        OpenApiParameter(**PARAM_DATA_INICIAL),
        OpenApiParameter(**PARAM_DATA_FINAL),
    ],
    responses={201: "result"},
    examples=[OpenApiExample(**RESPONSE_DEFAULT)]
)

SCHEMA_ONLY_DRE = extend_schema(
    parameters=[OpenApiParameter(**PARAM_DRE_UUI)],
    responses={201: "result"},
    examples=[OpenApiExample(**RESPONSE_DEFAULT)]
)

SCHEMA_ONLY_RESPONSE_MSG = extend_schema(
    responses={201: "result"},
    examples=[OpenApiExample(**RESPONSE_DEFAULT)]
)

DOCS = dict(
    demonstrativos_financeiros=SCHEMA_DEFAULT,
    creditos=SCHEMA_DEFAULT,
    unidades=SCHEMA_DEFAULT,
    materiais_e_servicos=SCHEMA_ONLY_DATES,
    status_prestacoes_contas=SCHEMA_DEFAULT,
    saldos_finais_periodos=SCHEMA_DEFAULT,
    relacao_bens=SCHEMA_DEFAULT,
    devolucao_ao_tesouro_prestacao_conta=SCHEMA_DEFAULT,
    rateios=SCHEMA_DEFAULT,
    atas=SCHEMA_DEFAULT,
    documentos_despesas=SCHEMA_DEFAULT,
    contas_associacao=SCHEMA_DEFAULT,
    repasses=SCHEMA_DEFAULT,
    dados_membros_apm=SCHEMA_ONLY_DATES,
    processos_sei_regularidade=SCHEMA_ONLY_RESPONSE_MSG,
    processos_sei_prestacao_contas=SCHEMA_ONLY_DRE,
    associacoes=SCHEMA_DEFAULT,
    saldos_bancarios=SCHEMA_DEFAULT,
)
