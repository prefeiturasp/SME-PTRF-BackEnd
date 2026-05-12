from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers.consolidado_dre_serializer import (
    ConsolidadoDreSerializer,
    ConsolidadoDreDetalhamentoSerializer,
)

from ...serializers.ata_parecer_tecnico_serializer import (
    AtaParecerTecnicoLookUpSerializer,
)


PARAM_DRE = {
    "name": "dre",
    "description": "UUID da DRE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_PERIODO = {
    "name": "periodo",
    "description": "UUID do período.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ATA = {
    "name": "ata",
    "description": "UUID da Ata de Parecer Técnico.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_UUID = {
    "name": "uuid",
    "description": "UUID do Consolidado DRE.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ANALISE_ATUAL = {
    "name": "analise_atual",
    "description": "UUID da análise atual.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_ADD_APROVADAS_RESSALVA = {
    "name": "add_aprovadas_ressalva",
    "description": "Adicionar aprovadas com ressalva.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_STATUS_SME = {
    "name": "status_sme",
    "description": "Lista de status SME separados por vírgula.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_TIPO_RELATORIO = {
    "name": "tipo_relatorio",
    "description": "Tipo do relatório.",
    "required": False,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

PARAM_LAUDA = {
    "name": "lauda",
    "description": "UUID da lauda.",
    "required": False,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}


SCHEMA_LIST = extend_schema(
    description=(
        "Lista consolidados DRE.\n\n"
        "Permite filtros por DRE e período."
    ),
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_PERIODO),
    ],
    responses={
        200: ConsolidadoDreSerializer(many=True),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description="Retorna os detalhes de um Consolidado DRE.",
    tags=["Consolidados DRE"],
    responses={
        200: ConsolidadoDreSerializer,
        404: OpenApiResponse(
            description="Consolidado DRE não encontrado."
        ),
    },
)

SCHEMA_CRIAR_ATA_E_ATRELAR = extend_schema(
    description=(
        "Cria uma ata e atrela ao consolidado DRE."
    ),
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: AtaParecerTecnicoLookUpSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
    },
)

SCHEMA_CONSOLIDADOS_DRE_POR_ATA = extend_schema(
    description=(
        "Retorna o consolidado DRE a partir do UUID da ata."
    ),
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_ATA),
    ],
    responses={
        200: ConsolidadoDreSerializer,
    },
)

SCHEMA_PUBLICADOS_E_PROXIMA_PUBLICACAO = extend_schema(
    description=(
        "Retorna consolidados já publicados e próxima publicação."
    ),
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_PERIODO),
    ],
)

SCHEMA_GERAR_PREVIA = extend_schema(
    description="Gera prévia do consolidado DRE.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: ConsolidadoDreSerializer,
    },
)

SCHEMA_PUBLICAR = extend_schema(
    description="Publica o consolidado DRE.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
    responses={
        200: ConsolidadoDreSerializer,
    },
)

SCHEMA_STATUS_RELATORIO_PUBLICACOES = extend_schema(
    description=(
        "Retorna o status do relatório consolidado "
        "de publicações parciais."
    ),
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_PERIODO),
    ],
)

SCHEMA_DOCUMENTOS = extend_schema(
    description="Retorna os documentos do consolidado.",
    tags=["Consolidados DRE"],
)

SCHEMA_STATUS_CONSOLIDADO = extend_schema(
    description="Retorna o status do consolidado DRE.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_PERIODO),
    ],
)

SCHEMA_DOWNLOAD_RELATORIO = extend_schema(
    description="Realiza download do relatório consolidado.",
    tags=["Consolidados DRE"],
    responses={
        200: OpenApiResponse(description="Arquivo PDF."),
    },
)

SCHEMA_DOWNLOAD_ATA = extend_schema(
    description="Realiza download da ata de parecer técnico.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_ATA),
    ],
)

SCHEMA_DOWNLOAD_LAUDA = extend_schema(
    description="Realiza download da lauda.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_LAUDA),
    ],
)

SCHEMA_TRILHA_STATUS = extend_schema(
    description="Retorna a trilha de status.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_PERIODO),
        OpenApiParameter(**PARAM_ADD_APROVADAS_RESSALVA),
    ],
)

SCHEMA_DETALHAMENTO = extend_schema(
    description="Retorna detalhamento do consolidado.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_UUID),
    ],
    responses={
        200: ConsolidadoDreDetalhamentoSerializer,
    },
)

SCHEMA_DETALHAMENTO_CONFERENCIA = extend_schema(
    description="Retorna detalhamento para conferência de documentos.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_UUID),
        OpenApiParameter(**PARAM_ANALISE_ATUAL),
    ],
)

SCHEMA_ACOMPANHAMENTO_RELATORIOS = extend_schema(
    description="Acompanhamento de relatórios consolidados SME.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO),
    ],
)

SCHEMA_LISTAGEM_STATUS = extend_schema(
    description="Listagem de relatórios consolidados SME por status.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_PERIODO),
        OpenApiParameter(**PARAM_DRE),
        OpenApiParameter(**PARAM_TIPO_RELATORIO),
        OpenApiParameter(**PARAM_STATUS_SME),
    ],
)

SCHEMA_DEVOLVER = extend_schema(
    description="Devolve um consolidado DRE.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_MARCAR_PUBLICADO = extend_schema(
    description="Marca relatório como publicado no diário oficial.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_MARCAR_NAO_PUBLICADO = extend_schema(
    description="Marca relatório como não publicado.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_REABRIR = extend_schema(
    description="Reabre um consolidado DRE.",
    tags=["Consolidados DRE"],
    parameters=[
        OpenApiParameter(**PARAM_UUID),
    ],
)

SCHEMA_ANALISAR = extend_schema(
    description="Coloca consolidado em análise.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_MARCAR_ANALISADO = extend_schema(
    description="Marca consolidado como analisado.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_PCS_CONSOLIDADO = extend_schema(
    description="Lista PCs vinculadas ao consolidado.",
    tags=["Consolidados DRE"],
)

SCHEMA_PCS_RETIFICAVEIS = extend_schema(
    description="Lista PCs retificáveis.",
    tags=["Consolidados DRE"],
)

SCHEMA_PCS_EM_RETIFICACAO = extend_schema(
    description="Lista PCs em retificação.",
    tags=["Consolidados DRE"],
)

SCHEMA_RETIFICAR = extend_schema(
    description="Retifica consolidado DRE.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_DESFAZER_RETIFICACAO = extend_schema(
    description="Desfaz retificação.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_UPDATE_RETIFICACAO = extend_schema(
    description="Atualiza retificação.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

SCHEMA_UPDATE_MOTIVO_RETIFICACAO = extend_schema(
    description="Atualiza motivo da retificação.",
    tags=["Consolidados DRE"],
    request=OpenApiTypes.OBJECT,
)

DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    criar_ata_e_atrelar_consolidado_dre=SCHEMA_CRIAR_ATA_E_ATRELAR,
    consolidados_dre_por_ata_uuid=SCHEMA_CONSOLIDADOS_DRE_POR_ATA,
    consolidados_dre_ja_criados_e_proxima_criacao=SCHEMA_PUBLICADOS_E_PROXIMA_PUBLICACAO,
    gerar_previa_consolidado_dre=SCHEMA_GERAR_PREVIA,
    publicar=SCHEMA_PUBLICAR,
    retornar_status_relatorio_consolidado_de_publicacoes_parciais=SCHEMA_STATUS_RELATORIO_PUBLICACOES,
    documentos=SCHEMA_DOCUMENTOS,
    status_consolidado_dre=SCHEMA_STATUS_CONSOLIDADO,
    download_relatorio_consolidado=SCHEMA_DOWNLOAD_RELATORIO,
    download_ata_parecer_tecnico=SCHEMA_DOWNLOAD_ATA,
    download_lauda=SCHEMA_DOWNLOAD_LAUDA,
    trilha_de_status=SCHEMA_TRILHA_STATUS,
    detalhamento_relatorio_consolidado=SCHEMA_DETALHAMENTO,
    detalhamento_relatorio_consolidado_conferencia_documentos=SCHEMA_DETALHAMENTO_CONFERENCIA,
    acompanhamento_de_relatorios_consolidados_sme=SCHEMA_ACOMPANHAMENTO_RELATORIOS,
    listagem_de_relatorios_consolidados_sme_por_status=SCHEMA_LISTAGEM_STATUS,
    devolver=SCHEMA_DEVOLVER,
    marcar_como_publicado_no_diario_oficial=SCHEMA_MARCAR_PUBLICADO,
    marcar_como_nao_publicado_no_diario_oficial=SCHEMA_MARCAR_NAO_PUBLICADO,
    reabrir=SCHEMA_REABRIR,
    analisar=SCHEMA_ANALISAR,
    marcar_como_analisado=SCHEMA_MARCAR_ANALISADO,
    pcs_do_consolidado=SCHEMA_PCS_CONSOLIDADO,
    pcs_retificaveis=SCHEMA_PCS_RETIFICAVEIS,
    pcs_em_retificacao=SCHEMA_PCS_EM_RETIFICACAO,
    retificar=SCHEMA_RETIFICAR,
    desfazer_retificacao=SCHEMA_DESFAZER_RETIFICACAO,
    update_retificacao=SCHEMA_UPDATE_RETIFICACAO,
    update_motivo_retificacao=SCHEMA_UPDATE_MOTIVO_RETIFICACAO,
)
