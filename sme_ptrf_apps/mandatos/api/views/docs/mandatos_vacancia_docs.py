from drf_spectacular.utils import extend_schema

from sme_ptrf_apps.mandatos.api.serializers.mandato_serializer import MandatoSerializer

SCHEMA_MANDATO_VIGENTE = extend_schema(
    description="Retorna o mandato vigente",
    tags=["Histórico de Membros (v2)"],
    responses={
        200: MandatoSerializer,
    },
)

SCHEMA_MANDATOS_ANTERIORES = extend_schema(
    description="Lista os mandatos anteriores ao mandato vigente.",
    tags=["Histórico de Membros (v2)"],
    responses={
        200: MandatoSerializer(many=True),
    },
)

DOCS = dict(
    mandato_vigente=SCHEMA_MANDATO_VIGENTE,
    mandatos_anteriores=SCHEMA_MANDATOS_ANTERIORES,
)
