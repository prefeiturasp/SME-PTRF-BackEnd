from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from sme_ptrf_apps.situacao_patrimonial.api.serializers import (
    BemProduzidoSaveRacunhoSerializer,
)

TAG = ["Situação Patrimonial - Bem Produzido (Rascunho)"]

SCHEMA_CREATE = extend_schema(
    description=(
        "Cria um bem produzido em modo rascunho.\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    request=BemProduzidoSaveRacunhoSerializer,
    responses={
        201: BemProduzidoSaveRacunhoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
    },
)

SCHEMA_PARTIAL_UPDATE = extend_schema(
    description=(
        "Atualiza parcialmente um bem produzido em rascunho.\n\n"
        "**Requer autenticação.**"
    ),
    tags=TAG,
    request=BemProduzidoSaveRacunhoSerializer,
    responses={
        200: BemProduzidoSaveRacunhoSerializer,
        400: OpenApiResponse(description="Dados inválidos."),
        404: OpenApiResponse(description="Não encontrado."),
    },
)

DOCS_BEM_PRODUZIDO_RASCUNHO = dict(
    create=SCHEMA_CREATE,
    partial_update=SCHEMA_PARTIAL_UPDATE,
)
