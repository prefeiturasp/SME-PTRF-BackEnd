from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from sme_ptrf_apps.mandatos.api.serializers import (MandatoVigenteComComposicoesSerializer, MandatoSerializer,
                                                    MandatoComComposicoesSerializer)


PARAM_ASSOCIACAO_UUID = {
    "name": 'associacao_uuid',
    "description": 'Filtro de uuid de Associação',
    "required": True,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

PARAM_EDITAVEL_UUID = {
    "name": 'associacao_uuid',
    "description": 'Filtro de uuid de Associação',
    "required": True,
    "allow_blank": True,
    "type": OpenApiTypes.UUID,
    "location": OpenApiParameter.QUERY,
}

SCHEMA_MANDATO_VIGENTE = extend_schema(
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
    ],
    responses={200: MandatoVigenteComComposicoesSerializer},
)

SCHEMA_MANDATOS_ANTERIORES = extend_schema(
    responses={200: MandatoSerializer},
)

SCHEMA_MANDATO_ANTERIOR = extend_schema(
    parameters=[
        OpenApiParameter(**PARAM_ASSOCIACAO_UUID),
    ],
    responses={200: MandatoComComposicoesSerializer},
)


SCHEMA_MANDATO_MAIS_RECENTE = extend_schema(
    responses={200: MandatoSerializer},
)


DOCS = dict(
    mandato_vigente=SCHEMA_MANDATO_VIGENTE,
    mandatos_anteriores=SCHEMA_MANDATOS_ANTERIORES,
    mandato_anterior=SCHEMA_MANDATO_ANTERIOR,
    mandato_mais_recente=SCHEMA_MANDATO_MAIS_RECENTE,
)
