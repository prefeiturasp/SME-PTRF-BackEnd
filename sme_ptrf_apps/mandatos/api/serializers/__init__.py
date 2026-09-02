# flake8: noqa
from .mandato_serializer import MandatoSerializer, MandatoVigenteComComposicoesSerializer, \
    MandatoComComposicoesSerializer
from .composicao_serializer import ComposicaoSerializer, ComposicaoComCargosSerializer
from .ocupante_cargo_serializer import OcupanteCargoSerializer, OcupanteCargoCreateSerializer
from .cargo_composicao_serializer import CargoComposicaoSerializer, CargoComposicaoLookupSerializer, \
    CargoComposicaoCreateSerializer
from .cargo_composicao_vacancia_serializer import (
    CargoComposicaoVacanciaCreateSerializer,
    RegistrarSaidaSerializer,
    CargoComposicaoVacanciaSerializer,
    CargoComposicaoVacanciaEditarOcupanteSerializer
)