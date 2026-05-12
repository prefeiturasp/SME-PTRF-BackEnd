from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from sme_ptrf_apps.core.api.serializers.associacao_serializer import (
    AssociacaoCompletoSerializer,
    AssociacaoCreateSerializer,
    AssociacaoListSerializer,
    AssociacaoSerializer,
    AssociacaoUpdateSerializer,
)

from sme_ptrf_apps.core.api.serializers.ata_serializer import (
    AtaLookUpSerializer,
)

from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import (
    ContaAssociacaoDadosSerializer,
)

from sme_ptrf_apps.core.api.serializers.periodo_serializer import (
    PeriodoLookUpSerializer,
)

from sme_ptrf_apps.core.api.serializers.processo_associacao_serializer import (
    ProcessoAssociacaoRetrieveSerializer,
)

from sme_ptrf_apps.paa.api.serializers import PaaSerializer

PARAM_PAGE = {
    "name": "page",
    "description": "Número da página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_PAGE_SIZE = {
    "name": "page_size",
    "description": "Quantidade de itens por página.",
    "required": False,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_NOME = {
    "name": "nome",
    "description": (
        "Filtra pelo nome da associação, "
        "nome da unidade ou código EOL."
    ),
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_DRE_UUID = {
    "name": "unidade__dre__uuid",
    "description": "UUID da DRE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_UNIDADE = {
    "name": "unidade__tipo_unidade",
    "description": "Tipo da unidade.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_FILTRO_INFORMACOES = {
    "name": "filtro_informacoes",
    "description": (
        "Filtra pelas tags de informações "
        "da associação."
    ),
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO_UUID = {
    "name": "periodo_uuid",
    "description": "UUID do período.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA = {
    "name": "data",
    "description": "Data da consulta.",
    "required": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_ALL = {
    "name": "all",
    "description": (
        "Quando informado retorna todas as contas "
        "independente do recurso."
    ),
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_ANALISE_PRESTACAO_UUID = {
    "name": "analise_prestacao_uuid",
    "description": "UUID da análise da prestação.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ASSOCIACAO_UUID = {
    "name": "associacao_uuid",
    "description": "UUID da associação.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS_PC = {
    "name": "status_pc",
    "description": "Status da prestação de contas.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_CODIGO_EOL = {
    "name": "codigo_eol",
    "description": "Código EOL da unidade.",
    "required": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_ANO = {
    "name": "ano",
    "description": "Ano da consulta.",
    "required": True,
    "type": OpenApiTypes.INT,
    "location": OpenApiParameter.QUERY,
}

PARAM_RECURSO_UUID = {
    "name": "recurso_uuid",
    "description": "UUID do recurso.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_IGNORAR_DEVOLVIDAS = {
    "name": "ignorar_devolvidas",
    "description": "Ignora prestações devolvidas.",
    "required": False,
    "type": OpenApiTypes.BOOL,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA_ENCERRAMENTO = {
    "name": "data_de_encerramento",
    "description": "Data de encerramento.",
    "required": True,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO_INICIAL = {
    "name": "periodo_inicial",
    "description": "UUID do período inicial.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DRE_UUID_OBRIGATORIO = {
    "name": "dre_uuid",
    "description": "UUID da DRE.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS_REGULARIDADE = {
    "name": "status_regularidade",
    "description": "Status da regularidade.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_LIST = extend_schema(
    description=(
        "Lista paginada de associações.\n\n"
        "Permite filtros por nome, DRE, tipo de unidade "
        "e tags de informações."
    ),
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PAGE),
        OpenApiParameter(**PARAM_PAGE_SIZE),
        OpenApiParameter(**PARAM_NOME),
        OpenApiParameter(**PARAM_DRE_UUID),
        OpenApiParameter(**PARAM_TIPO_UNIDADE),
        OpenApiParameter(**PARAM_FILTRO_INFORMACOES),
    ],
    responses={
        200: AssociacaoListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description=(
        "Retorna os detalhes completos de uma associação."
    ),
    tags=["Associações"],
    responses={
        200: AssociacaoCompletoSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        403: OpenApiResponse(
            description="You do not have permission to perform this action."
        ),
        404: OpenApiResponse(
            description="Associação não encontrada."
        ),
    },
)

SCHEMA_CREATE = extend_schema(
    description="Cria uma nova associação.",
    tags=["Associações"],
    request=AssociacaoCreateSerializer,
    responses={
        201: AssociacaoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Atualiza completamente uma associação."
    ),
    tags=["Associações"],
    request=AssociacaoUpdateSerializer,
    responses={
        200: AssociacaoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Associação não encontrada."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente uma associação."
    ),
    tags=["Associações"],
    request=AssociacaoUpdateSerializer,
    responses={
        200: AssociacaoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Associação não encontrada."),
    },
)

SCHEMA_DESTROY = extend_schema(
    description="Exclui uma associação.",
    tags=["Associações"],
    responses={
        204: OpenApiResponse(
            description="Associação excluída com sucesso."
        ),
        400: OpenApiResponse(
            description="Não é possível excluir associação com movimentações."
        ),
        404: OpenApiResponse(
            description="Associação não encontrada."
        ),
    },
)

SCHEMA_REPASSES_PENDENTES = extend_schema(
    description="Retorna repasses pendentes por período.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Período obrigatório."),
        404: OpenApiResponse(description="Período não encontrado."),
    },
)

SCHEMA_PAINEL_ACOES = extend_schema(
    description="Retorna painel resumido de ações.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_STATUS_PERIODO = extend_schema(
    description="Retorna status do período.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_DATA),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_PERMITE_IMPLANTACAO_SALDOS = extend_schema(
    description="Verifica se permite implantação de saldos.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_IMPLANTACAO_SALDOS = extend_schema(
    description="Retorna implantação de saldos.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_IMPLANTA_SALDOS = extend_schema(
    description="Implanta saldos da associação.",
    tags=["Associações"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Erro na implantação."),
    },
)

SCHEMA_CONTAS = extend_schema(
    description="Lista contas da associação.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO_UUID),
        OpenApiParameter(**PARAM_ALL),
    ],
    responses={
        200: ContaAssociacaoDadosSerializer(many=True),
    },
)

SCHEMA_CONTAS_ENCERRADAS = extend_schema(
    description="Lista contas encerradas.",
    tags=["Associações"],
    responses={
        200: ContaAssociacaoDadosSerializer(many=True),
    },
)

SCHEMA_CONTAS_ACERTOS = extend_schema(
    description="Lista contas com acertos em lançamentos.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_ANALISE_PRESTACAO_UUID),
    ],
    responses={
        200: ContaAssociacaoDadosSerializer(many=True),
    },
)

SCHEMA_CONTAS_ACERTOS_DESPESAS = extend_schema(
    description=(
        "Lista contas com acertos em despesas "
        "de períodos anteriores."
    ),
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_ANALISE_PRESTACAO_UUID),
    ],
    responses={
        200: ContaAssociacaoDadosSerializer(many=True),
    },
)

SCHEMA_CONTAS_UPDATE = extend_schema(
    description="Atualiza contas da associação.",
    tags=["Associações"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Erro de validação."),
    },
)

SCHEMA_TABELAS = extend_schema(
    description="Retorna tabelas auxiliares.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            "Resposta",
            value={
                "tipos_unidade": [],
                "dres": [],
                "filtro_informacoes": [],
            },
        ),
    ],
)

SCHEMA_EXPORTAR = extend_schema(
    description="Exporta XLSX da associação.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.BINARY,
    },
)

SCHEMA_EXPORTAR_PDF = extend_schema(
    description="Exporta PDF da associação.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.BINARY,
    },
)

SCHEMA_PERIODOS_PRESTACAO = extend_schema(
    description="Lista períodos para prestação de contas.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_IGNORAR_DEVOLVIDAS),
    ],
    responses={
        200: PeriodoLookUpSerializer(many=True),
    },
)

SCHEMA_PERIODOS_ATE_AGORA = extend_schema(
    description="Lista períodos até agora fora implantação.",
    tags=["Associações"],
    responses={
        200: PeriodoLookUpSerializer(many=True),
    },
)

SCHEMA_STATUS_PRESTACOES = extend_schema(
    description="Lista status das prestações.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_STATUS_PC),
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_PROCESSOS = extend_schema(
    description="Lista processos da associação.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_RECURSO_UUID),
    ],
    responses={
        200: ProcessoAssociacaoRetrieveSerializer(many=True),
    },
)

SCHEMA_CONSULTA_EOL = extend_schema(
    description="Consulta unidade pelo código EOL.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_CODIGO_EOL),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Código inválido."),
    },
)

SCHEMA_STATUS_PRESIDENTE = extend_schema(
    description="Retorna status do presidente.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_UPDATE_STATUS_PRESIDENTE = extend_schema(
    description="Atualiza status do presidente.",
    tags=["Associações"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiResponse(description="Erro de validação."),
    },
)

SCHEMA_LISTA_REGULARIDADE = extend_schema(
    description="Lista regularidade das associações no ano.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_ANO),
        OpenApiParameter(**PARAM_DRE_UUID_OBRIGATORIO),
        OpenApiParameter(**PARAM_NOME),
        OpenApiParameter(**PARAM_TIPO_UNIDADE),
        OpenApiParameter(**PARAM_STATUS_REGULARIDADE),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_VERIFICACAO_REGULARIDADE = extend_schema(
    description="Retorna verificação de regularidade.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_ANO),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_ATUALIZA_ITENS_VERIFICACAO = extend_schema(
    description="Atualiza itens de verificação.",
    tags=["Associações"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_PREVIA_ATA = extend_schema(
    description="Retorna prévia da ata.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: AtaLookUpSerializer,
        404: OpenApiResponse(description="Prévia não encontrada."),
    },
)

SCHEMA_VALIDA_DATA_ENCERRAMENTO = extend_schema(
    description="Valida data de encerramento.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_DATA_ENCERRAMENTO),
        OpenApiParameter(**PARAM_PERIODO_INICIAL),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_TAGS_INFORMACOES = extend_schema(
    description="Lista tags de informações.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_STATUS_CADASTRO = extend_schema(
    description="Retorna pendências cadastrais.",
    tags=["Associações"],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_CONTAS_DO_PERIODO = extend_schema(
    description="Lista contas do período.",
    tags=["Associações"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO_UUID),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
    },
)

SCHEMA_PAA_VIGENTE = extend_schema(
    description="Retorna o PAA vigente.",
    tags=["Associações"],
    responses={
        200: PaaSerializer,
        404: OpenApiResponse(description="PAA não encontrado."),
    },
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    destroy=SCHEMA_DESTROY,
    repasses_pendentes_por_periodo=SCHEMA_REPASSES_PENDENTES,
    painel_acoes=SCHEMA_PAINEL_ACOES,
    status_periodo=SCHEMA_STATUS_PERIODO,
    permite_implantacao_saldos=SCHEMA_PERMITE_IMPLANTACAO_SALDOS,
    implantacao_saldos=SCHEMA_IMPLANTACAO_SALDOS,
    implanta_saldos=SCHEMA_IMPLANTA_SALDOS,
    contas=SCHEMA_CONTAS,
    contas_encerradas=SCHEMA_CONTAS_ENCERRADAS,
    contas_com_acertos_em_lancamentos=SCHEMA_CONTAS_ACERTOS,
    contas_com_acertos_em_despesas_periodos_anteriores=SCHEMA_CONTAS_ACERTOS_DESPESAS,
    contas_update=SCHEMA_CONTAS_UPDATE,
    tabelas=SCHEMA_TABELAS,
    exportar=SCHEMA_EXPORTAR,
    exportarpdf=SCHEMA_EXPORTAR_PDF,
    periodos_para_prestacao_de_contas=SCHEMA_PERIODOS_PRESTACAO,
    periodos_ate_agora_fora_implantacao=SCHEMA_PERIODOS_ATE_AGORA,
    status_prestacoes=SCHEMA_STATUS_PRESTACOES,
    processos_da_associacao=SCHEMA_PROCESSOS,
    consulta_unidade=SCHEMA_CONSULTA_EOL,
    get_status_presidente=SCHEMA_STATUS_PRESIDENTE,
    update_status_presidente=SCHEMA_UPDATE_STATUS_PRESIDENTE,
    lista_regularidade_no_ano=SCHEMA_LISTA_REGULARIDADE,
    verificacao_regularidade=SCHEMA_VERIFICACAO_REGULARIDADE,
    atualiza_itens_verificacao=SCHEMA_ATUALIZA_ITENS_VERIFICACAO,
    previa_ata=SCHEMA_PREVIA_ATA,
    valida_data_de_encerramento=SCHEMA_VALIDA_DATA_ENCERRAMENTO,
    tags_informacoes_list=SCHEMA_TAGS_INFORMACOES,
    status_cadastro=SCHEMA_STATUS_CADASTRO,
    contas_do_periodo=SCHEMA_CONTAS_DO_PERIODO,
    paa_vigente=SCHEMA_PAA_VIGENTE,
)
