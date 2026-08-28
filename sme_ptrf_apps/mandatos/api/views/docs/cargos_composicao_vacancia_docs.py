from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
)

from ...serializers import (
    CargoComposicaoVacanciaSerializer,
    CargoComposicaoVacanciaCreateSerializer,
    CargoComposicaoVacanciaEditarOcupanteSerializer,
    RegistrarSaidaSerializer,
)

TAGS = ["Histórico de Membros (v2)"]

PARAM_COMPOSICAO_UUID = {
    "name": "composicao_uuid",
    "description": "UUID da composição (v2) para filtrar os cargos associados.",
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

PARAM_MANDATO_UUID = {
    "name": "mandato_uuid",
    "description": "UUID do mandato.",
    "required": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_DATA = {
    "name": "data",
    "description": "Data de referência (formato YYYY-MM-DD) do snapshot da composição. Padrão: hoje.",
    "required": False,
    "type": OpenApiTypes.DATE,
    "location": OpenApiParameter.QUERY,
}

PARAM_CARGO_ASSOCIACAO_UUID = {
    "name": "cargo_associacao_uuid",
    "description": "Cargo da associação (choices fixos, ex.: PRESIDENTE_DIRETORIA_EXECUTIVA) cuja timeline será retornada.",
    "required": True,
    "type": OpenApiTypes.STR,
    "location": OpenApiParameter.QUERY,
}

DESCRICAO_BASE = (
    "\nschema e regras próprios, atrás da flag `historico-de-membros-v2`."
)

SCHEMA_LIST = extend_schema(
    description="Retorna uma lista paginada de registros de cargo/vacância (v2)." + DESCRICAO_BASE,
    tags=TAGS,
    responses={
        200: CargoComposicaoVacanciaSerializer(many=True),
    },
)

SCHEMA_RETRIEVE = extend_schema(
    description="Retorna os detalhes de um registro de cargo/vacância (v2) identificado pelo UUID." + DESCRICAO_BASE,
    tags=TAGS,
    responses={
        200: CargoComposicaoVacanciaSerializer,
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_CREATE = extend_schema(
    description=(
        "Registra a entrada de um ocupante em um cargo — cria o registro de ocupação e, se necessário, "
        "fecha/ajusta a vacância aberta ou detecta substituição direta do ocupante anterior."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=CargoComposicaoVacanciaCreateSerializer,
    responses={
        201: CargoComposicaoVacanciaCreateSerializer,
        400: OpenApiResponse(description="Dados inválidos ou regra de negócio de entrada violada."),
    },
)

SCHEMA_UPDATE = extend_schema(
    description=(
        "Edita os dados cadastrais do ocupante de um registro existente (nome, telefone, etc.). "
        "Nunca altera cargo, datas ou vínculo de substituição — bloqueado em registro vago."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=CargoComposicaoVacanciaEditarOcupanteSerializer,
    responses={
        200: CargoComposicaoVacanciaEditarOcupanteSerializer,
        400: OpenApiResponse(description="Dados inválidos ou registro vago."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description="Igual ao PUT — edição de dados do ocupante aceita atualização parcial." + DESCRICAO_BASE,
    tags=TAGS,
    request=CargoComposicaoVacanciaEditarOcupanteSerializer,
    responses={
        200: CargoComposicaoVacanciaEditarOcupanteSerializer,
        400: OpenApiResponse(description="Dados inválidos ou registro vago."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_COMPOSICAO_VIGENTE = extend_schema(
    description=(
        "Retorna o UUID da composição (v2) de uma associação+mandato, criando-a (get-or-create) "
        "se ainda não existir."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
        OpenApiParameter(**PARAM_MANDATO_UUID),
    ],
    responses={
        200: OpenApiResponse(description="Ex.: {\"uuid\": \"...\"}"),
    },
)

SCHEMA_REGISTRAR_SAIDA = extend_schema(
    description=(
        "Registra a saída do ocupante vigente de um registro. A data informada é o primeiro dia em que "
        "o ocupante já não está mais presente (o sistema grava o dia anterior como fim do intervalo) e "
        "abre, na mesma operação, uma vacância cobrindo do dia seguinte até o fim do mandato."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=RegistrarSaidaSerializer,
    responses={
        200: CargoComposicaoVacanciaSerializer,
        400: OpenApiResponse(description="Data inválida ou registro não está ocupado e vigente."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_COMPOSICAO_POR_DATA = extend_schema(
    description=(
        "Retorna o snapshot completo da composição (um registro por cargo do catálogo, ocupado ou vago) "
        "em uma data específica. Aceita `composicao_uuid` OU `associacao_uuid`+`data`."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    parameters=[
        OpenApiParameter(**{**PARAM_COMPOSICAO_UUID, "required": False}),
        OpenApiParameter(**{**PARAM_ASSOCIACAO_UUID, "required": False}),
        OpenApiParameter(**{**PARAM_DATA, "required": True}),
    ],
    responses={
        200: OpenApiResponse(description="Dicionário {cargo_associacao: CargoComposicaoVacancia | null}."),
        404: OpenApiResponse(description="Composição não encontrada."),
    },
)

SCHEMA_DATAS_DE_ALTERACAO = extend_schema(
    description=(
        "Retorna os \"marcos\" de navegação da composição: a união ordenada, sem repetição, das datas de "
        "início de todos os registros (ocupados e vagos) de todos os cargos."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    parameters=[
        OpenApiParameter(**PARAM_COMPOSICAO_UUID),
    ],
    responses={
        200: OpenApiResponse(description="Lista de datas ISO (YYYY-MM-DD), ordenada. Ex.: [\"2026-01-01\", \"2026-04-01\"]."),
        404: OpenApiResponse(description="Composição não encontrada."),
    },
)

SCHEMA_CANCELAR_SAIDA = extend_schema(
    description=(
        "Reverte uma saída já registrada, devolvendo o registro ao estado vigente e removendo a vacância "
        "aberta criada por aquela saída. Bloqueado se o registro já está vigente (nada a cancelar) ou se "
        "já existe um sucessor direto vinculado."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=None,
    responses={
        200: CargoComposicaoVacanciaSerializer,
        400: OpenApiResponse(description="Registro já vigente ou já possui sucessor direto."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_CORRIGIR_SAIDA = extend_schema(
    description=(
        "Corrige a data de uma saída já registrada — cancela e registra a saída novamente com a nova data, "
        "de forma atômica, reaplicando todas as validações de saída."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=RegistrarSaidaSerializer,
    responses={
        200: CargoComposicaoVacanciaSerializer,
        400: OpenApiResponse(description="Data inválida ou operação bloqueada (ex.: já existe sucessor)."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)

SCHEMA_TIMELINE = extend_schema(
    description=(
        "Retorna todo o histórico (ocupações e vacâncias) de um cargo dentro de uma composição, "
        "ordenado cronologicamente."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    parameters=[
        OpenApiParameter(**PARAM_COMPOSICAO_UUID),
        OpenApiParameter(**PARAM_CARGO_ASSOCIACAO_UUID),
    ],
    responses={
        200: CargoComposicaoVacanciaSerializer(many=True),
        404: OpenApiResponse(description="Composição não encontrada."),
    },
)

SCHEMA_CARGOS_DA_COMPOSICAO = extend_schema(
    description=(
        "Monta o board de cargos da composição em uma data de referência, no mesmo formato usado pela v1 "
        "(`{diretoria_executiva, conselho_fiscal}`, um item por cargo do catálogo) — inclui os campos "
        "`cargo_vago`, `cargo_vago_vigente` e `ocupante_vigente`, que não existem na v1."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    parameters=[
        OpenApiParameter(**PARAM_COMPOSICAO_UUID),
        OpenApiParameter(**PARAM_DATA),
    ],
    responses={
        200: OpenApiResponse(description="Dicionário {diretoria_executiva: [...], conselho_fiscal: [...]}."),
        404: OpenApiResponse(description="Composição não encontrada."),
    },
)

SCHEMA_CANCELAR_ENTRADA = extend_schema(
    description=(
        "Desfaz uma entrada vigente (nenhum sucessor registrado depois dela) como se nunca tivesse "
        "acontecido: o registro é apagado e o que existia antes dele é restaurado — o ocupante substituído "
        "diretamente volta a vigente, ou a vacância anterior é estendida de volta até o fim do mandato. "
        "É o caminho para desfazer uma cadeia de substituições, já que `cancelar-saida` é bloqueado "
        "quando já existe um sucessor."
    ) + DESCRICAO_BASE,
    tags=TAGS,
    request=None,
    responses={
        204: OpenApiResponse(description="Entrada cancelada — registro removido, sem corpo de resposta."),
        400: OpenApiResponse(description="Registro não está ocupado e vigente."),
        404: OpenApiResponse(description="Registro não encontrado."),
    },
)


DOCS = dict(
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
    composicao_vigente=SCHEMA_COMPOSICAO_VIGENTE,
    registrar_saida=SCHEMA_REGISTRAR_SAIDA,
    composicao_por_data=SCHEMA_COMPOSICAO_POR_DATA,
    datas_de_alteracoes_na_composicao=SCHEMA_DATAS_DE_ALTERACAO,
    cancelar_saida=SCHEMA_CANCELAR_SAIDA,
    corrigir_data_saida=SCHEMA_CORRIGIR_SAIDA,
    timeline=SCHEMA_TIMELINE,
    cargos_da_composicao=SCHEMA_CARGOS_DA_COMPOSICAO,
    cancelar_entrada=SCHEMA_CANCELAR_ENTRADA,
)
