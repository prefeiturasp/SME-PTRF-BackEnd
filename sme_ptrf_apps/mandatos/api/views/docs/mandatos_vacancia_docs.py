from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from sme_ptrf_apps.mandatos.api.serializers.mandato_vacancia_serializer import MandatoVacanciaSerializer


SCHEMA_MANDATO_VIGENTE = extend_schema(
    description="Retorna o mandato vigente",
    responses={
        200: MandatoVacanciaSerializer,
    },
)

SCHEMA_MANDATOS_ANTERIORES = extend_schema(
    description="Lista os mandatos anteriores ao mandato vigente.",
    responses={
        200: MandatoVacanciaSerializer(many=True),
    },
)
SCHEMA_MANDATO_MAIS_RECENTE = extend_schema(
    description="Retorna o mandato mais recente cadastrado (usado pela tela de parametrização de Mandatos da SME).",
    responses={
        200: MandatoVacanciaSerializer,
    },
)

SCHEMA_LIST = extend_schema(
    description="Lista os mandatos cadastrados, paginado.",
    parameters=[
        OpenApiParameter(name="referencia", type=OpenApiTypes.STR, required=False,
                          description="Filtra pela referência do mandato (ex.: '2023 a 2025')."),
    ],
    responses={200: MandatoVacanciaSerializer(many=True)},
)

SCHEMA_RETRIEVE = extend_schema(
    description="Retorna os detalhes de um mandato.",
    responses={200: MandatoVacanciaSerializer},
)

SCHEMA_CREATE = extend_schema(
    description="Cria um novo período de mandato.",
    responses={201: MandatoVacanciaSerializer},
)

SCHEMA_UPDATE = extend_schema(
    description="Edita um período de mandato existente.",
    responses={200: MandatoVacanciaSerializer},
)

SCHEMA_DESTROY = extend_schema(
    description=(
        "Exclui um período de mandato. Só permite excluir o mandato mais recente, e só se não "
        "houver nenhum cargo ocupado (v2) vinculado a ele."
    ),
    responses={204: None},
)

DOCS = dict(
    mandato_vigente=SCHEMA_MANDATO_VIGENTE,
    mandatos_anteriores=SCHEMA_MANDATOS_ANTERIORES,
    mandato_mais_recente=SCHEMA_MANDATO_MAIS_RECENTE,
    list=SCHEMA_LIST,
    retrieve=SCHEMA_RETRIEVE,
    create=SCHEMA_CREATE,
    update=SCHEMA_UPDATE,
    partial_update=SCHEMA_UPDATE,
    destroy=SCHEMA_DESTROY,
)
